from .tree import _print_dir_tree
from . import util

import os
import dill
import time


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


class ExpStruct:

    _DATA_FILE = '.data'
    _TIME_FILE = '.time'

    @staticmethod
    def __load_time(location_dir):
        fp = os.path.join(location_dir, ExpStruct._TIME_FILE)
        with open(fp, 'rb') as f:
            time = dill.load(f)
        return time

    @staticmethod
    def _save_data(location_dir, data):
        fp = os.path.join(location_dir, ExpStruct._DATA_FILE)
        with open(fp, 'wb') as f:
            dill.dump(data, f)
        fp = os.path.join(location_dir, ExpStruct._TIME_FILE)
        with open(fp, 'wb') as f:
            dill.dump(time.time(), f)
        # TODO ??? save data structure version to the separated file `version.pkl`, it will help to
        #  recognize unmatched versions of saved file and xman data structure and maybe it will be
        #  possible to make some converters from old to the newest versions.

    @staticmethod
    def _load_data(location_dir):
        fp = os.path.join(location_dir, ExpStruct._DATA_FILE)
        with open(fp, 'rb') as f:
            data = dill.load(f)
        return data

    @staticmethod
    def _make(data_class, struct_class, location_dir, name, descr):
        location_dir = util._make_dir(location_dir)
        data = data_class(name, descr)
        ExpStruct._save_data(location_dir, data)
        struct = struct_class(location_dir, data)
        return struct

    @staticmethod
    def _load(struct_class, location_dir):
        data = ExpStruct._load_data(location_dir)
        struct = struct_class(location_dir, data)
        return struct

    def __init__(self, location_dir, data):
        self.location_dir = location_dir
        self.data = data
        self.num = util._get_dir_num(location_dir)
        self.status = None
        self.__time = None
        self._update()

    def __str__(self):
        raise NotImplementedError(f"`__str__` method should be overriden!")

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle):
        p.text(str(self) if not cycle else '...')

    # TODO check if I need force
    def _update(self, force=False):
        t = ExpStruct.__load_time(self.location_dir)
        if not force and self.__time == t:
            return False
        self.__time = t
        return True

    def _save(self):
        ExpStruct._save_data(self.location_dir, self.data)
        self._update()

    def tree(self):
        self._update()
        _print_dir_tree(self.location_dir)

    def info(self):
        self._update()
        print(self)

    def start(self):
        raise NotImplementedError(f"`start` method should be overriden!")


# class ExpStructBox(ExpStruct):
#
#     def __init__(self):
#         super
