import os
from typing import Optional, Type, Callable, Any, Tuple
from copy import deepcopy

from .error import NotExistsXManError, ArgumentsXManError, AlreadyExistsXManError
from . import util, filesystem, tree, confirm
from .note import Note


class ExpStructData:

    def __init__(self, name: str, descr: str):
        self.name: str = name
        self.descr: str = descr
        self.manual_status: str = None
        self.manual_status_resolution: str = None
        self.result_stringifier: Callable[[Any], str] = None
        self.result_viewer: Callable[[Any], None] = None


class ExpStructStatus:

    EMPTY = 'EMPTY'
    TO_DO = 'TO_DO'
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'
    ERROR = 'ERROR'
    SUCCESS = 'SUCCESS'
    FAIL = 'FAIL'

    __WORKFLOW = (EMPTY, TO_DO, IN_PROGRESS, (DONE, ERROR), (SUCCESS, FAIL))

    @staticmethod
    def has_status(status_str: str):
        return util.check_has_value_in_class_public_constants(status_str, ExpStructStatus)

    @staticmethod
    def _check(status_str, resolution):
        ExpStructStatus.has_status(status_str)
        if status_str in (ExpStructStatus.SUCCESS, ExpStructStatus.FAIL) and resolution is None:
            raise ArgumentsXManError(f"SUCCESS and FAIL manual statuses "
                                     f"require setting resolutions!")

    @staticmethod
    def _fit_parameters(status_obj, status_str, resolution, manual):
        return status_obj is not None and status_obj.status_str == status_str \
                and status_obj.resolution == resolution and status_obj.manual == manual

    @property
    def status_str(self) -> str: return self.__status_str

    @property
    def resolution(self) -> str: return self.__resolution

    @property
    def manual(self) -> bool: return self.__manual

    @property
    def workflow(self) -> Tuple[str | Tuple[str, str]]: return deepcopy(ExpStructStatus.__WORKFLOW)

    @property
    def next(self) -> Optional[str]:
        if ExpStructStatus.__WORKFLOW[-1] == self.status_str:
            return None
        for i, it in enumerate(ExpStructStatus.__WORKFLOW[:-1]):
            if it == self.status_str or (type(it) is tuple and self.status_str in it):
                return ExpStructStatus.__WORKFLOW[i + 1]

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle):
        p.text(str(self) if not cycle else '...')

    def __init__(self, status: str, resolution: str = None, manual: bool = False):
        ExpStructStatus._check(status, resolution)
        self.__status_str = status
        self.__resolution = resolution
        self.__manual = manual

    def __str__(self): return self.status_str + ' *' if self.manual else self.status_str


class ExpStruct:

    _AUTO_STATUS_RESOLUTION = '-= auto status =-'

    @property
    def api(self): return self._api

    @property
    def location_dir(self) -> str: return self.__location_dir

    @property
    def parent(self) -> Type['ExpGroup | ExpProj']: return self._parent

    @property
    def num(self) -> int: return self.__num

    @property
    def name(self) -> str: return self._data.name

    @property
    def descr(self) -> str: return self._data.descr

    @property
    def status(self) -> ExpStructStatus: return self.__status

    @property
    def is_manual(self) -> bool: return self._data.manual_status is not None

    @property
    def result_stringifier(self) -> Callable[[Any], str]:
        return self._data.result_stringifier

    @result_stringifier.setter
    def result_stringifier(self, value: Callable[[Any], str]):
        self._data.result_stringifier = value
        self._save()

    @property
    def result_viewer(self) -> Callable[[Any], None]: return self._data.result_viewer

    @result_viewer.setter
    def result_viewer(self, value: Callable[[Any], None]):
        self._data.result_viewer = value
        self._save()

    @property
    def note(self) -> Note:
        if self.__note is None:
            self.__note = Note(self.location_dir)
        return self.__note

    def tree(self, depth: int = None): tree.print_dir_tree(self.location_dir, depth)

    def info(self):
        text = str(self)
        if self.status.resolution is not None:
            text += util.tab(f"\nResolution: {self.status.resolution}")
        if self.note.has_any:
            text += util.tab(f"\nNotes: {self.note.get_existence_str()}")
        return text

    def set_manual_status(self, status: str, resolution: str) -> 'ExpStruct':
        ExpStructStatus._check(status, resolution)
        self._data.manual_status = status
        self._data.manual_status_resolution = resolution
        self._save()
        return self

    def success(self, resolution: str) -> Optional['ExpStruct']:
        return self.set_manual_status(ExpStructStatus.SUCCESS, resolution)

    def fail(self, resolution: str) -> Optional['ExpStruct']:
        return self.set_manual_status(ExpStructStatus.FAIL, resolution)

    def delete_manual_status(self, need_confirm: bool = True) -> Optional['ExpStruct']:
        if not self.status.manual:
            raise NotExistsXManError(f"There's no manual status in the struct `{self}`")
        if confirm.request(need_confirm,
                            f"ATTENTION! Do you want to delete the manual status "
                            f"`{self._data.manual_status}`\nand its resolution "
                            f"`{self._data.manual_status_resolution}`\nof exp `{self}`?"):
            self._data.manual_status = None
            self._data.manual_status_resolution = None
            self._save()
            return self
        return None

    def edit(self, name: Optional[str] = None, descr: Optional[str] = None):
        need_save = False
        if self._data.name != name:
            if self._parent is not None and self._parent.has_child(name):
                raise AlreadyExistsXManError(
                    f"There's another child with the name=`{name}` "
                    f"in the parent `{self._parent}`")
            self._data.name = name
            need_save = True
        if self._data.descr != descr:
            self._data.descr = descr
            need_save = True
        if need_save:
            self._save()

    def update(self):
        if self.__updating:
            return
        self.__updating = True
        self._data, self.__time = filesystem.load_fresh_data_and_time(self.location_dir,
                                                                      self._data, self.__time)
        # Status should be updated at the end of the inherited updating hierarchy
        if type(self) == ExpStruct:
            self._update_status()
        self.__updating = False

    def _change_location_dir(self, new_location_dir):
        self.__location_dir = os.path.normpath(new_location_dir)
        self.__num = filesystem.get_dir_num(new_location_dir)

    def _update_status(self):
        if self.is_manual:
            status, resolution = self._data.manual_status, self._data.manual_status_resolution
        else:
            status, resolution = self._process_auto_status()
        if not ExpStructStatus._fit_parameters(self.status, status, resolution, self.is_manual):
            self.__status = ExpStructStatus(status, resolution, self.is_manual)

    def _process_auto_status(self): util.override_it()

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle): p.text(str(self) if not cycle else '...')

    def _save(self): self.__time = filesystem.save_data_and_time(self.location_dir, self._data)

    def _destroy(self):
        self._api._obj = None
        self._api = None
        self._parent = None
        self._data = None
        self.__status = None

    def __init__(self, location_dir, parent):
        from .structbox import ExpStructBox
        from .api import ExpStructAPI
        self.__location_dir = None
        self.__num = None
        self._change_location_dir(location_dir)
        self._parent: ExpStructBox = parent
        self._data: ExpStructData = None
        self.__time = None
        self.__status = None
        self.__note: Note = None
        self.__updating = False
        self.update()
        self._api: ExpStructAPI = None

    def __str__(self): util.override_it()
