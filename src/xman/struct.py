from .event import EventDispatcher, Event
from .tree import print_dir_tree
from .error import NotExistsXManError, ArgumentsXManError, AlreadyExistsXManError
from . import util

import time


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
        util.check_has_value_in_class_public_constants(status, ExpStructStatus)
        if status in (ExpStructStatus.SUCCESS, ExpStructStatus.FAIL) and resolution is None:
            raise ArgumentsXManError(f"SUCCESS and FAIL manual statuses require setting resolutions!")

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

    STRUCT_EDITED = 'STRUCT_EDITED'
    CHANGE_NAME_REQUESTED = 'CHANGE_NAME_REQUESTED'
    STATUS_CHANGED = 'STATUS_CHANGED'

    def __init__(self, target, kind, request=None):
        super().__init__(target, kind)
        self.request = request 
        self.respondent = None
        self.response = None


class ExpStruct(EventDispatcher):

    _DATA_FILE = '.data'
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
        elif name is None and descr is None:
            self._update()
        else:
            raise ArgumentsXManError(f"`name` and `descr` should be both None or not None at the same time!")

    def __str__(self): util.override_it()

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
            self._dispatch(ExpStructEvent, ExpStructEvent.STATUS_CHANGED)

    def _process_auto_status(self): util.override_it()

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle): p.text(str(self) if not cycle else '...')

    def _update(self):
        if self.__updating:
            return
        self.__updating = True
        t = util.load(self.location_dir, ExpStruct.__TIME_FILE)
        if self.__time != t:
            self.__time = t
            self._data = util.load(self.location_dir, ExpStruct._DATA_FILE)
        # Status should be updated at the end of the inherited updating hierarchy
        if type(self) == ExpStruct:
            self._update_status()
        self.__updating = False

    def _save_and_update(self):
        util.save(self._data, self.location_dir, ExpStruct._DATA_FILE)
        self.__time = time.time()
        util.save(self.__time, self.location_dir, ExpStruct.__TIME_FILE)
        self._update()

    def _info(self):
        text = str(self)
        if self.status.resolution:
            text += util.tab(f"\nResolution: {self.status.resolution}")
        return text

    def destroy(self):
        # TODO Implement for all inheritance chain
        super()._destroy()

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
            raise NotExistsXManError(f"There's no manual status in exp `{self}`")
        if not confirm or util.response(f"ACHTUNG! Remove the manual status `{self._data.manual_status}` of exp `{self}`?"):
            self._data.manual_status = None
            self._data.manual_status_resolution = None
            self._save_and_update()
            return self
        return None

    def edit(self, name=None, descr=None):
        need_update = need_save = False
        if self._data.name != name:
            event = self._dispatch(ExpStructEvent, ExpStructEvent.CHANGE_NAME_REQUESTED, request=name)
            if event is not None and not event.response:
                raise AlreadyExistsXManError(f"There's another child with the name=`{name}` in the parent `{event.respondent}`")
            self._data.name = name
            need_update = need_save = True
        if self._data.descr != descr:
            self._data.descr = descr
            need_save = True
        if need_save:
            self._save_and_update()
        if need_update:
            self._dispatch(ExpStructEvent, ExpStructEvent.STRUCT_EDITED)
