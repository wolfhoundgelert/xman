import os

from .event import EventDispatcher, Event
from .error import NotExistsXManError, ArgumentsXManError, AlreadyExistsXManError
from . import util, filesystem, tree, confirm


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
            raise ArgumentsXManError(f"SUCCESS and FAIL manual statuses "
                                     f"require setting resolutions!")

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

    @property
    def name(self) -> str:
        self._update()
        return self._name

    @property
    def descr(self) -> str:
        self._update()
        return self._descr

    @property
    def status(self) -> ExpStructStatus:
        self._update()
        return self._status

    @property
    def manual(self) -> bool:
        self._update()
        return self._manual

    def tree(self):
        self._update()
        self._tree()

    def info(self):
        self._update()
        text = self._info()
        print(text)

    def start(self):
        self._update()
        self._start()

    def set_manual_status(self, status: str, resolution: str) -> 'ExpStruct':
        self._update()
        return self._set_manual_status(status, resolution)

    def delete_manual_status(self, need_confirm=True):
        self._update()
        if confirm._request(need_confirm,
                            f"ATTENTION! Remove the manual status `{self._data.manual_status}` "
                            f"of exp `{self}`?"):
            return self._delete_manual_status()
        return None

    def edit(self, name=None, descr=None):
        self._update()
        self._edit(name, descr)

    _AUTO_STATUS_RESOLUTION = '-= auto status =-'

    @property
    def _name(self) -> str:
        return self._data.name

    @property
    def _descr(self) -> str:
        return self._data.descr

    @property
    def _status(self):
        return self.__status

    @property
    def _manual(self):
        return self._data.manual_status is not None

    def _tree(self):
        tree.print_dir_tree(self.location_dir)

    def _info(self):
        text = str(self)
        if self._status.resolution:
            text += util.tab(f"\nResolution: {self._status.resolution}")
        return text

    def _start(self):
        util.override_it()

    def _set_manual_status(self, status: str, resolution: str) -> 'ExpStruct':
        ExpStructStatus._check(status, resolution)
        self._data.manual_status = status
        self._data.manual_status_resolution = resolution
        self._save_and_update()
        return self

    def _delete_manual_status(self) -> 'ExpStruct':
        if not self._status.manual:
            raise NotExistsXManError(f"There's no manual status in the struct `{self}`")
        self._data.manual_status = None
        self._data.manual_status_resolution = None
        self._save_and_update()
        return self

    def _edit(self, name=None, descr=None):
        need_update = need_save = False
        if self._data.name != name:
            event = self._dispatch(ExpStructEvent, ExpStructEvent.CHANGE_NAME_REQUESTED,
                                   request=name)
            if event is not None and not event.response:
                raise AlreadyExistsXManError(
                    f"There's another child with the name=`{name}` "
                    f"in the parent `{event.respondent}`")
            self._data.name = name
            need_update = need_save = True
        if self._data.descr != descr:
            self._data.descr = descr
            need_save = True
        if need_save:
            self._save_and_update()
        if need_update:
            self._dispatch(ExpStructEvent, ExpStructEvent.STRUCT_EDITED)

    def _update_status(self):
        if self._manual:
            status, resolution = self._data.manual_status, self._data.manual_status_resolution
        else:
            status, resolution = self._process_auto_status()
        if not ExpStructStatus._fit_parameters(self.__status, status, resolution, self._manual):
            self.__status = ExpStructStatus(status, resolution, self._manual)
            self._dispatch(ExpStructEvent, ExpStructEvent.STATUS_CHANGED)

    def _process_auto_status(self): util.override_it()

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle): p.text(str(self) if not cycle else '...')

    def _update(self):
        if self.__updating:
            return
        self.__updating = True
        self._data, self.__time = filesystem._load_fresh_data_and_time(self.location_dir,
                                                                       self._data, self.__time)
        # Status should be updated at the end of the inherited updating hierarchy
        if type(self) == ExpStruct:
            self._update_status()
        self.__updating = False

    def _save_and_update(self):
        self.__time = filesystem._save_data_and_time(self._data, self.location_dir)
        self._update()

    def _destroy(self):
        self._data = None
        self.__status = None
        super()._destroy()

    def __init__(self, location_dir):
        super().__init__()
        self.location_dir = os.path.normpath(location_dir)
        self.num = filesystem._get_dir_num(location_dir)
        self._data = None
        self.__time = None
        self.__status = None
        self.__updating = False
        self._update()

    def __str__(self): util.override_it()
