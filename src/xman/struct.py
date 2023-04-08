from .family import Child, Parent
from .tree import _print_dir_tree
from . import util

# import pickle
# import dill as pickle
import cloudpickle as pickle
import os
import time
import shutil
from abc import ABC, abstractmethod


class ExpStructData:

    def __init__(self, name, descr):
        self.name = name
        self.descr = descr
        self.manual_status = None
        self.manual_status_resolution = None


# TODO support it
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
        self.workflow = self._workflow()
        self.__check(status, resolution)
        self.status = status
        self.current = status  # just for logical support for `next`
        self.next = self.__next()
        self.resolution = resolution
        self.manual = manual

    def __str__(self):
        return self.status

    def __call__(self):
        return self.status

    def __check(self, status, resolution):
        if not ExpStructStatus.__has_workflow_status(self.workflow, status):
            raise ValueError(f"The workflow `{self.workflow}` doesn't have status `{status}`!")
        if status in (ExpStructStatus.SUCCESS, ExpStructStatus.FAIL) and resolution is None:
            raise ValueError(f"SUCCESS and FAIL manual statuses require setting resolutions!")

    def __next(self):
        if self.workflow[-1] == self.status:
            return None
        for i, it in enumerate(self.workflow[:-1]):
            if it == self.status or (type(it) is tuple and self.status in it):
                return self.workflow[i + 1]

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle):
        p.text(str(self) if not cycle else '...')

    def _workflow(self):
        return (
            ExpStructStatus.EMPTY,
            ExpStructStatus.TODO,
            ExpStructStatus.IN_PROGRESS,
            (ExpStructStatus.DONE, ExpStructStatus.ERROR),
            (ExpStructStatus.SUCCESS, ExpStructStatus.FAIL)
        )


class ExpStruct(Child, ABC):

    __DATA_FILE = '.data'
    __TIME_FILE = '.time'

    _AUTO_STATUS_RESOLUTION = '-= auto status =-'

    @staticmethod
    @abstractmethod
    def _dir_prefix():
        pass

    def __init__(self, location_dir, name, descr):
        ABC.__init__(self)
        Child.__init__(self)
        self.location_dir = location_dir
        self.num = util.get_dir_num(location_dir)
        self.status = None
        self.__time = None
        if name is not None and descr is not None:  # make a new data
            util.make_dir(location_dir)
            self.data = self._data_class(name, descr)
            self._save()
        self._update()

    def __str__(self):
        raise NotImplementedError(f"`__str__` method should be overriden!")

    def __load_data(self):
        fp = os.path.join(self.location_dir, ExpStruct.__DATA_FILE)
        with open(fp, 'rb') as f:
            self.data = pickle.load(f)

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
            self.__load_data()
            self.__time == t

    def _save(self):
        fp = os.path.join(self.location_dir, ExpStruct.__DATA_FILE)
        with open(fp, 'wb') as f:
            pickle.dump(self.data, f)
        fp = os.path.join(self.location_dir, ExpStruct.__TIME_FILE)
        with open(fp, 'wb') as f:
            pickle.dump(time.time(), f)

    def tree(self):
        self._update()
        _print_dir_tree(self.location_dir)

    def info(self):
        self._update()
        print(self)

    @abstractmethod
    def start(self):
        pass


class ExpStructBox(ExpStruct, Parent, ABC):

    def __init__(self, location_dir, name, descr):
        self.__inited = False
        ABC.__init__(self)
        Parent.__init__(self)
        ExpStruct.__init__(self, location_dir, name, descr)
        self.__num_to_child = {}
        self.__name_to_child = {}
        self.__inited = True
        self._update()

    def __children_has_status(self, status_or_list, all: bool):
        status = status_or_list if type(status_or_list) is str else None
        status_list = status_or_list if type(status_or_list) is list else None
        for child in self.children():
            s = child.status()
            if status:
                if all:
                    if s != status:
                        return False
                else:
                    if s == status:
                        return True
            else:
                if all:
                    if s not in status_list:
                        return False
                else:
                    if s in status_list:
                        return True
        return True if all else False

    def __process_status(self):
        if self.data.manual_status is not None:
            status = self.data.manual_status
            resolution = self.data.manual_status_resolution
            manual = True
        else:
            resolution = ExpStruct._AUTO_STATUS_RESOLUTION
            manual = False
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
            elif self.__children_has_status(
                    [ExpStructStatus.DONE, ExpStructStatus.SUCCESS, ExpStructStatus.FAIL], True):
                status = ExpStructStatus.DONE
            else:
                status = ExpStructStatus.IN_PROGRESS
        self.status = ExpStructStatus(status, resolution, manual)

    @abstractmethod
    def _get_child_class(self):
        pass

    def _get_child_dir(self, num):
        return os.path.join(self.location_dir, self._get_child_class()._dir_prefix() + str(num))

    def _update(self):
        if not self.__inited:
            return
        super()._update()
        child_class = self._get_child_class()
        child_dir_prefix = child_class._dir_prefix()
        nums = util.get_dir_nums_by_pattern(self.location_dir, child_dir_prefix)
        for num in nums:
            if num not in self.__num_to_child:
                location_dir = self._get_child_dir(num)
                child = child_class(location_dir, None, None)
                self.add(child)
        for child in self.children():
            if child.num not in nums:
                self.remove(child)
        for child in self.children():
            child._update()
        self.__process_status()

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
        self.add(child)
        # self.root._update()  # TODO looks like I don't need it
        return child

    def _remove_child(self, num_or_name):
        self._update()
        child = self._get_child_by_num_or_name(num_or_name)
        child_dir = self._get_child_dir(child.num)
        response = input(f"ACHTUNG! Remove `{child_dir}` dir with all its content? (y/n) ")
        if response.lower() != "y":
            return
        self.remove(child)
        shutil.rmtree(child_dir)
        # self.root._update()  # TODO looks like I don't need it

    def add(self, child):
        super().add(child)
        self.__num_to_child[child.num] = child
        self.__name_to_child[child.data.name] = child

    def remove(self, child):
        super().remove(child)
        del self.__num_to_child[child.num]
        del self.__name_to_child[child.data.name]
