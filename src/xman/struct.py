from .event import EventDispatcher, Event
from .tree import print_dir_tree
from . import util

import cloudpickle as pickle  # dill as pickle, pickle
import os
import time
import shutil


class ExpStructData:

    def __init__(self, name, descr):
        self.name = name
        self.descr = descr
        self.manual_status = None
        self.manual_status_resolution = None


class ExpStructStatus:

    EMPTY = 'EMPTY'
    TODO = 'TODO'
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'
    ERROR = 'ERROR'
    SUCCESS = 'SUCCESS'
    FAIL = 'FAIL'

    __WORKFLOW = (EMPTY, TODO, IN_PROGRESS, (DONE, ERROR), (SUCCESS, FAIL))

    @staticmethod
    def __has_status_in_workflow(status):
        for it in ExpStructStatus.__WORKFLOW:
            if it == status or status in it:
                return True
        return False

    @staticmethod
    def _check(status, resolution):
        if not ExpStructStatus.__has_status_in_workflow(status):
            raise ValueError(f"The workflow `{ExpStructStatus.__WORKFLOW}` doesn't have status `{status}`!")
        if status in (ExpStructStatus.SUCCESS, ExpStructStatus.FAIL) and resolution is None:
            raise ValueError(f"SUCCESS and FAIL manual statuses require setting resolutions!")

    @staticmethod
    def _fit_parameters(status_obj, status, resolution, manual):
        return status_obj is not None and status_obj.status == status \
                and status_obj.resolution == resolution and status_obj.manual == manual

    def __init__(self, status: str, resolution: str = None, manual: bool = False):
        ExpStructStatus._check(status, resolution)
        self.status = status
        self.resolution = resolution
        self.manual = manual

    def __str__(self): return self.status + ' *' if self.manual else self.status

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle): p.text(str(self) if not cycle else '...')

    @property
    def workflow(self): return ExpStructStatus.__WORKFLOW.copy()

    @property
    def next(self):
        if ExpStructStatus.__WORKFLOW[-1] == self.status:
            return None
        for i, it in enumerate(ExpStructStatus.__WORKFLOW[:-1]):
            if it == self.status or (type(it) is tuple and self.status in it):
                return ExpStructStatus.__WORKFLOW[i + 1]


class ExpStructEvent(Event):

    EDIT_STRUCT = 'EDIT_STRUCT'
    REQUEST_CHANGE_NAME = 'REQUEST_CHANGE_NAME'
    UPDATE_STATUS = 'UPDATE_STATUS'

    _KINDS = [EDIT_STRUCT, REQUEST_CHANGE_NAME, UPDATE_STATUS]

    def __init__(self, target, kind, request=None):
        super().__init__(target)
        self.kind = kind
        self._check_kind()
        self.request = request 
        self.respondent = None
        self.response = None

    def _check_kind(self):
        if self.kind not in self._KINDS:
            raise ValueError(f"Wrong type `{self.kind}`, should be one of `{self._KINDS}`")


class ExpStruct(EventDispatcher):

    __DATA_FILE = '.data'
    __TIME_FILE = '.time'

    _AUTO_STATUS_RESOLUTION = '-= auto status =-'

    @staticmethod
    def _dir_prefix(): util.override_it()

    def __init__(self, location_dir, name, descr):
        super().__init__()
        self.location_dir = location_dir
        self.num = util.get_dir_num(location_dir)
        self.__status = None
        self.__time = None
        self.__updating = False
        if name is not None and descr is not None:  # make a new data
            util.make_dir(location_dir)
            self._data = self._data_class(name, descr)
            self._save_and_update()
        else:
            self._update()

    def __str__(self): util.override_it()

    def __load_data(self):
        fp = os.path.join(self.location_dir, ExpStruct.__DATA_FILE)
        with open(fp, 'rb') as f:
            loaded_data = pickle.load(f)
            self._on_load_data(loaded_data)

    @property
    def _data_class(self): return ExpStructData

    @property
    def _status(self): return self.__status

    def _update_status(self):
        manual = self._data.manual_status is not None
        if manual:
            status, resolution = self._data.manual_status, self._data.manual_status_resolution
        else:
            status, resolution = self._process_auto_status()
        if not ExpStructStatus._fit_parameters(self.__status, status, resolution, manual):
            self.__status = ExpStructStatus(status, resolution, manual)
            self._dispatch(ExpStructEvent, ExpStructEvent.UPDATE_STATUS)

    def _process_auto_status(self): util.override_it()

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle): p.text(str(self) if not cycle else '...')

    def _update(self):
        if self.__updating:
            return
        self.__updating = True
        fp = os.path.join(self.location_dir, ExpStruct.__TIME_FILE)
        with open(fp, 'rb') as f:
            t = pickle.load(f)
        if self.__time != t:
            self.__time = t
            self.__load_data()
        # Status should be updated at the end of the inherited updating hierarchy
        if type(self) == ExpStruct:
            self._update_status()
        self.__updating = False

    # Can be overriden in descendants
    def _on_load_data(self, loaded_data): self._data = loaded_data

    def _save_and_update(self):
        fp = os.path.join(self.location_dir, ExpStruct.__DATA_FILE)
        with open(fp, 'wb') as f:
            pickle.dump(self._data, f)
        fp = os.path.join(self.location_dir, ExpStruct.__TIME_FILE)
        with open(fp, 'wb') as f:
            self.__time = time.time()
            pickle.dump(self.__time, f)
        self._update()

    def _info(self):
        text = str(self)
        if self.status.resolution:
            text += util.tab(f"\nResolution: {self.status.resolution}")
        return text

    @property
    def name(self):
        self._update()
        return self._data.name

    @property
    def descr(self):
        self._update()
        return self._data.descr

    @property
    def status(self):
        self._update()
        return self._status

    def tree(self):
        self._update()
        print_dir_tree(self.location_dir)

    def info(self):
        self._update()
        text = self._info()
        print(text)

    def start(self): util.override_it()

    def set_manual_status(self, status: str, resolution: str):
        self._update()
        ExpStructStatus._check(status, resolution)
        self._data.manual_status = status
        self._data.manual_status_resolution = resolution
        self._save_and_update()
        return self

    def delete_manual_status(self, confirm=True):
        self._update()
        if not self._status.manual:
            raise AssertionError(f"There's no manual status in exp `{self}`")
        if not confirm or util.response(f"ACHTUNG! Remove the manual status `{self._data.manual_status}` of exp `{self}`?"):
            self._data.manual_status = None
            self._data.manual_status_resolution = None
            self._save_and_update()
            return self
        return None

    def edit(self, name=None, descr=None):
        need_update = need_save = False
        if self._data.name != name:
            event = self._dispatch(ExpStructEvent, ExpStructEvent.REQUEST_CHANGE_NAME, request=name)
            if event is not None and not event.response:
                raise ValueError(f"There's another child with the name=`{name}` in the parent `{event.respondent}`")
            self._data.name = name
            need_update = need_save = True
        if self._data.descr != descr:
            self._data.descr = descr
            need_save = True
        if need_save:
            self._save_and_update()
        if need_update:
            self._dispatch(ExpStructEvent, ExpStructEvent.EDIT_STRUCT)


class ExpStructBoxEvent(ExpStructEvent):

    MAKE_CHILD = 'MAKE_CHILD'
    DESTROY_CHIlD = 'DESTROY_CHIlD'

    _KINDS = [MAKE_CHILD, DESTROY_CHIlD]


class ExpStructBox(ExpStruct):

    def __init__(self, location_dir, name, descr):
        self.__num_to_child = {}
        self.__name_to_child = {}
        self.__updating = False
        super().__init__(location_dir, name, descr)

    def __children_has_status(self, status_or_list, all_children: bool):
        sl = status_or_list if type(status_or_list) is list else [status_or_list]
        for child in self._children():
            s = child._status.status
            if all_children:
                if s not in sl:
                    return False
            else:
                if s in sl:
                    return True
        return True if all_children else False

    def __add(self, child):
        self.__num_to_child[child.num] = child
        self.__name_to_child[child._data.name] = child
        child._add_listener(ExpStructEvent, self._ExpStructEvent_listener)
        if isinstance(child, ExpStructBox):
            child._add_listener(ExpStructBoxEvent, self._ExpStructBoxEvent_listener)

    def __remove(self, child):
        del self.__num_to_child[child.num]
        del self.__name_to_child[child._data.name]
        child._remove_listener(ExpStructEvent, self._ExpStructEvent_listener)
        if isinstance(child, ExpStructBox):
            child._remove_listener(ExpStructBoxEvent, self._ExpStructBoxEvent_listener)
        child._destroy()

    def _get_child_class(self): util.override_it()

    def _get_child_dir(self, num):
        return os.path.join(self.location_dir, self._get_child_class()._dir_prefix() + str(num))

    def _process_auto_status(self):
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
        elif self.__children_has_status([ExpStructStatus.DONE, ExpStructStatus.SUCCESS, ExpStructStatus.FAIL], True):
            status = ExpStructStatus.DONE
        else:
            status = ExpStructStatus.IN_PROGRESS
        return status, resolution

    def _update(self):
        if self.__updating:
            return
        self.__updating = True
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
        for name in list(self.__name_to_child.keys()):
            del self.__name_to_child[name]
        for child in self._children():
            self.__name_to_child[child._data.name] = child
            child._update()
        # Status should be updated at the end of the inherited updating hierarchy
        if type(self) == ExpStructBox:
            self._update_status()
        self.__updating = False

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
        self._dispatch(ExpStructBoxEvent, ExpStructBoxEvent.MAKE_CHILD)
        return child

    # TODO rename _destroy_child, destroy_exp, destroy_group
    def _destroy_child(self, num_or_name, confirm=True):
        self._update()
        child = self._get_child_by_num_or_name(num_or_name)
        child_dir = self._get_child_dir(child.num)
        if not confirm or util.response(f"ACHTUNG! Remove `{child}` and its `{child_dir}` dir with all its content?"):
            self.__remove(child)
            shutil.rmtree(child_dir)
            self._dispatch(ExpStructBoxEvent, ExpStructBoxEvent.DESTROY_CHIlD)
            return child
        return None

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
                if child._status.status == status:
                    return child
        return None

    def _info(self):
        text = super()._info()
        for child in self._children():
            text += util.tab(f"\n\n{child._info()}")
        return text

    def _ExpStructEvent_listener(self, event: ExpStructEvent):
        self._update()
        if event.kind == ExpStructEvent.REQUEST_CHANGE_NAME:
            event.respondent = self
            event.response = event.request not in self.__name_to_child

    def _ExpStructBoxEvent_listener(self, event: ExpStructBoxEvent): self._update()
