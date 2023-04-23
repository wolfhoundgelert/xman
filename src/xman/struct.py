from .tree import print_dir_tree
from . import util

# import pickle
# import dill as pickle
import cloudpickle as pickle  # TODO What is better here - dill or cloudpickle?
import os
import time
import shutil


class ExpStructData:

    def __init__(self, name, descr):
        self.name = name
        self.descr = descr
        self.manual_status = None
        self.manual_status_resolution = None


class InProgressType:

    ACTIVE = 'ACTIVE'
    IDLE = 'IDLE'
    UNKNOWN = 'UNKNOWN'


class ExpStructStatus:

    EMPTY = 'EMPTY'
    TODO = 'TODO'
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'
    ERROR = 'ERROR'
    SUCCESS = 'SUCCESS'
    FAIL = 'FAIL'

    @staticmethod
    def __has_workflow_status(workflow, status):
        for it in workflow:
            if it == status:
                return True
            if type(it) is tuple:
                if ExpStructStatus.__has_workflow_status(it, status):
                    return True
        return False

    def __init__(self, status: str, resolution: str = None, manual: bool = False):
        self.__check(status, resolution)
        self.status = status
        self.resolution = resolution
        self.manual = manual

    def __str__(self):
        return self.status + ' *' if self.manual else self.status

    def __call__(self):
        return self.__str__()

    def __check(self, status, resolution):
        if not ExpStructStatus.__has_workflow_status(self.workflow, status):
            raise ValueError(f"The workflow `{self.workflow}` doesn't have status `{status}`!")
        if status in (ExpStructStatus.SUCCESS, ExpStructStatus.FAIL) and resolution is None:
            raise ValueError(f"SUCCESS and FAIL manual statuses require setting resolutions!")

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle):
        p.text(str(self) if not cycle else '...')

    @property
    def workflow(self):
        return (
            ExpStructStatus.EMPTY,
            ExpStructStatus.TODO,
            ExpStructStatus.IN_PROGRESS,
            (ExpStructStatus.DONE, ExpStructStatus.ERROR),
            (ExpStructStatus.SUCCESS, ExpStructStatus.FAIL)
        )

    @property
    def next(self):
        if self.workflow[-1] == self.status:
            return None
        for i, it in enumerate(self.workflow[:-1]):
            if it == self.status or (type(it) is tuple and self.status in it):
                return self.workflow[i + 1]


class ExpStruct:

    __DATA_FILE = '.data'
    __TIME_FILE = '.time'

    _AUTO_STATUS_RESOLUTION = '-= auto status =-'

    @staticmethod
    def _dir_prefix():
        raise NotImplementedError("Should be overriden!")

    def __init__(self, location_dir, name, descr):
        self.location_dir = location_dir
        self.num = util.get_dir_num(location_dir)
        self.status = None
        self.__time = None
        if name is not None and descr is not None:  # make a new data
            util.make_dir(location_dir)
            self._data = self._data_class(name, descr)
            self._save()
        self._inited = True
        self._update()

    def __str__(self):
        raise NotImplementedError("Should be overriden!")

    def __load_data(self):
        fp = os.path.join(self.location_dir, ExpStruct.__DATA_FILE)
        with open(fp, 'rb') as f:
            loaded_data = pickle.load(f)
            self._on_load_data(loaded_data)

    @property
    def _data_class(self):
        return ExpStructData

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle):
        p.text(str(self) if not cycle else '...')

    def _update(self):
        fp = os.path.join(self.location_dir, ExpStruct.__TIME_FILE)
        with open(fp, 'rb') as f:
            t = pickle.load(f)
        if self.__time != t:
            self.__time = t
            self.__load_data()
        if self._data.manual_status is not None:
            self.status = ExpStructStatus(self._data.manual_status, self._data.manual_status_resolution, manual=True)

    def _on_load_data(self, loaded_data):  # Can be overriden in descendants
        self._data = loaded_data

    def _save(self):
        fp = os.path.join(self.location_dir, ExpStruct.__DATA_FILE)
        with open(fp, 'wb') as f:
            pickle.dump(self._data, f)
        fp = os.path.join(self.location_dir, ExpStruct.__TIME_FILE)
        with open(fp, 'wb') as f:
            self.__time = time.time()
            pickle.dump(self.__time, f)
        self._update()

    @property
    def name(self):
        return self._data.name

    @property
    def descr(self):
        return self._data.descr

    def tree(self):
        self._update()
        print_dir_tree(self.location_dir)

    def info(self):
        self._update()
        print(self)

    def start(self):
        raise NotImplementedError("Should be overriden!")

    def set_manual_status(self, status: str, resolution: str):
        self._update()
        self._data.manual_status = status
        self._data.manual_status_resolution = resolution
        self._save()

    def remove_manual_status(self):
        self._update()
        self._data.manual_status = None
        self._data.manual_status_resolution = None
        self._save()


class ExpStructBox(ExpStruct):

    def __init__(self, location_dir, name, descr):
        self.__inited = False
        super().__init__(location_dir, name, descr)
        self.__num_to_child = {}
        self.__name_to_child = {}
        self.__inited = True
        self._update()

    def __children_has_status(self, status_or_list, all_children: bool):
        sl = status_or_list if type(status_or_list) is list else [status_or_list]
        for child in self._children():
            s = child.status.status
            if all_children:
                if s not in sl:
                    return False
            else:
                if s in sl:
                    return True
        return True if all_children else False

    def __process_status(self):
        if self._data.manual_status is None:
            resolution = ExpStruct._AUTO_STATUS_RESOLUTION
            if self.__children_has_status(ExpStructStatus.ERROR, False):
                status = ExpStructStatus.ERROR
            elif self.__children_has_status(ExpStructStatus.IN_PROGRESS, False):
                status = ExpStructStatus.IN_PROGRESS
            elif self.__children_has_status(ExpStructStatus.EMPTY, True):
                status = ExpStructStatus.EMPTY
            elif self.__children_has_status(ExpStructStatus.TODO, True):
                status = ExpStructStatus.TODO
            elif self.__children_has_status(ExpStructStatus.DONE, True):
                status = ExpStructStatus.DONE
            elif self.__children_has_status(ExpStructStatus.SUCCESS, True):
                status = ExpStructStatus.SUCCESS
            elif self.__children_has_status(ExpStructStatus.FAIL, True):
                status = ExpStructStatus.FAIL
            elif self.__children_has_status([ExpStructStatus.EMPTY, ExpStructStatus.TODO], True):
                status = ExpStructStatus.TODO
            elif self.__children_has_status(
                    [ExpStructStatus.DONE, ExpStructStatus.SUCCESS, ExpStructStatus.FAIL], True):
                status = ExpStructStatus.DONE
            else:
                status = ExpStructStatus.IN_PROGRESS
            self.status = ExpStructStatus(status, resolution, manual=False)

    def __add(self, child):
        self.__num_to_child[child.num] = child
        self.__name_to_child[child._data.name] = child

    def __remove(self, child):
        del self.__num_to_child[child.num]
        del self.__name_to_child[child._data.name]

    def _get_child_class(self):
        raise NotImplementedError("Should be overriden!")

    def _get_child_dir(self, num):
        return os.path.join(self.location_dir, self._get_child_class()._dir_prefix() + str(num))

    def _update(self):
        if not self.__inited:
            return
        self.__inited = False
        super()._update()
        child_class = self._get_child_class()
        child_dir_prefix = child_class._dir_prefix()
        nums = util.get_dir_nums_by_pattern(self.location_dir, child_dir_prefix)
        for num in nums:
            if num not in self.__num_to_child:
                location_dir = self._get_child_dir(num)
                child = child_class(location_dir, None, None)
                self.__add(child)
        for child in self._children():
            if child.num not in nums:
                self.__remove(child)
        for child in self._children():
            child._update()
        self.__process_status()
        self.__inited = True

    def _has_child_num_or_name(self, num_or_name):
        self._update()
        if util.is_num(num_or_name):
            return num_or_name in self.__num_to_child
        elif util.is_name(num_or_name):
            return num_or_name in self.__name_to_child
        else:
            raise ValueError(f"`num_or_name` should be num >= 1 (int) or name (str), but `{num_or_name}` was given!")

    def _get_child_by_num_or_name(self, num_or_name):
        self._update()
        if util.is_num(num_or_name) and num_or_name in self.__num_to_child:
            return self.__num_to_child[num_or_name]
        elif util.is_name(num_or_name) and num_or_name in self.__name_to_child:
            return self.__name_to_child[num_or_name]
        raise ValueError(f"There's no item with num or name `{num_or_name}`!")

    def _get_child_highest_num(self):
        self._update()
        nums = self.__num_to_child.keys()
        return max(nums) if len(nums) else 0

    def _make_child(self, name, descr, num=None) -> ExpStruct:
        self._update()
        util.check_num(num, True)
        if self._has_child_num_or_name(name):
            raise ValueError(f"A child with the name `{name}` already exists!")
        if num is not None:
            if self._has_child_num_or_name(num):
                raise ValueError(f"A child with the num `{num}` already exists!")
        else:
            num = self._get_child_highest_num() + 1
        child_dir = self._get_child_dir(num)
        child_class = self._get_child_class()
        child = child_class(child_dir, name, descr)
        self.__add(child)
        return child

    def _remove_child(self, num_or_name):
        self._update()
        child = self._get_child_by_num_or_name(num_or_name)
        child_dir = self._get_child_dir(child.num)
        response = input(f"ACHTUNG! Remove `{child_dir}` dir with all its content? (y/n) ")
        if response.lower() != "y":
            return
        self.__remove(child)
        shutil.rmtree(child_dir)

    def _children(self):
        self._update()
        return list(self.__num_to_child.values())

    def _nums(self):
        self._update()
        return list(self.__num_to_child.keys())

    def _names(self):
        self._update()
        return list(self.__name_to_child.keys())

    def _get_child_by_status(self, status_or_list):
        sl = status_or_list if type(status_or_list) is list else [status_or_list]
        for status in sl:
            for child in self._children():
                if child.status.status == status:
                    return child
        return None
