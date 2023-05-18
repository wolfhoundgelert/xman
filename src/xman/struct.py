import os
from typing import Optional

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

    @property
    def workflow(self):
        return ExpStructStatus.__WORKFLOW.copy()

    @property
    def next(self) -> Optional[str]:
        if ExpStructStatus.__WORKFLOW[-1] == self.status:
            return None
        for i, it in enumerate(ExpStructStatus.__WORKFLOW[:-1]):
            if it == self.status or (type(it) is tuple and self.status in it):
                return ExpStructStatus.__WORKFLOW[i + 1]

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle):
        p.text(str(self) if not cycle else '...')

    def __init__(self, status: str, resolution: str = None, manual: bool = False):
        ExpStructStatus._check(status, resolution)
        self.status = status
        self.resolution = resolution
        self.manual = manual

    def __str__(self): return self.status + ' *' if self.manual else self.status


class ExpStruct:

    _AUTO_STATUS_RESOLUTION = '-= auto status =-'

    @property
    def api(self): return self._api

    @property
    def _location_dir(self) -> str: return self.__location_dir

    @property
    def _parent(self) -> 'ExpStructBox': return self.__parent

    @property
    def _num(self) -> int: return self.__num

    @property
    def _name(self) -> str: return self._data.name

    @property
    def _descr(self) -> str: return self._data.descr

    @property
    def _status(self) -> ExpStructStatus: return self.__status

    @property
    def _is_manual(self): return self._data.manual_status is not None

    def _tree(self): tree.print_dir_tree(self.__location_dir)

    def _info(self):
        text = str(self)
        if self._status.resolution:
            text += util.tab(f"\nResolution: {self._status.resolution}")
        return text

    def _start(self): util.override_it()

    def _set_manual_status(self, status: str, resolution: str) -> 'ExpStruct':
        ExpStructStatus._check(status, resolution)
        self._data.manual_status = status
        self._data.manual_status_resolution = resolution
        self._save()
        return self

    def _success(self, resolution: str) -> Optional['ExpStruct']:
        return self._set_manual_status(ExpStructStatus.SUCCESS, resolution)

    def _fail(self, resolution: str) -> Optional['ExpStruct']:
        return self._set_manual_status(ExpStructStatus.FAIL, resolution)

    def _delete_manual_status(self, need_confirm) -> Optional['ExpStruct']:
        if not self._status.manual:
            raise NotExistsXManError(f"There's no manual status in the struct `{self}`")
        if confirm._request(need_confirm,
                            f"ATTENTION! Do you want to delete the manual status "
                            f"`{self._data.manual_status}` and its resolution "
                            f"`{self._data.manual_status_resolution}` of exp `{self}`?"):
            self._data.manual_status = None
            self._data.manual_status_resolution = None
            self._save()
            return self
        return None

    def _edit(self, name=None, descr=None):
        need_save = False
        if self._data.name != name:
            if self.__parent is not None and self.__parent._has_child_num_or_name(name):
                raise AlreadyExistsXManError(
                    f"There's another child with the name=`{name}` "
                    f"in the parent `{self.__parent}`")
            self._data.name = name
            need_save = True
        if self._data.descr != descr:
            self._data.descr = descr
            need_save = True
        if need_save:
            self._save()

    def _update_status(self):
        if self._is_manual:
            status, resolution = self._data.manual_status, self._data.manual_status_resolution
        else:
            status, resolution = self._process_auto_status()
        if not ExpStructStatus._fit_parameters(self.__status, status, resolution, self._is_manual):
            self.__status = ExpStructStatus(status, resolution, self._is_manual)

    def _process_auto_status(self): util.override_it()

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle): p.text(str(self) if not cycle else '...')

    def _update(self):
        if self.__updating:
            return
        self.__updating = True
        self._data, self.__time = filesystem._load_fresh_data_and_time(self.__location_dir,
                                                                       self._data, self.__time)
        # Status should be updated at the end of the inherited updating hierarchy
        if type(self) == ExpStruct:
            self._update_status()
        self.__updating = False

    def _save(self): self.__time = filesystem._save_data_and_time(self._data, self.__location_dir)

    def _destroy(self):
        self._api._obj = None
        self._api = None
        self.__parent = None
        self._data = None
        self.__status = None

    def __init__(self, location_dir, parent):
        from .structbox import ExpStructBox
        from .api import ExpStructAPI
        self.__location_dir = None
        self.__num = None
        self.__attention__change_location_dir(location_dir)
        self.__parent: ExpStructBox = parent
        self._data: ExpStructData = None
        self.__time = None
        self.__status = None
        self.__updating = False
        self._update()
        self._api = None

    def __str__(self): util.override_it()

    def __attention__change_location_dir(self, new_location_dir):
        self.__location_dir = os.path.normpath(new_location_dir)
        self.__num = filesystem._get_dir_num(new_location_dir)

    def __attention__change_parent(self, new_parent):
        self.__parent = new_parent
