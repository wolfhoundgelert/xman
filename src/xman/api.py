from typing import Any, Optional, Callable

from . import tree, maker, filesystem
from .error import NotImplementedXManError, IllegalOperationXManError
from .pipeline import CheckpointsMediator
from .exp import Exp
from .struct import ExpStructStatus, ExpStruct


def _get_exps_apis(exps): return [exp.api for exp in exps]


def _get_groups_apis(groups): return [group.api for group in groups]


class ExpStructStatusAPI:

    EMPTY = 'EMPTY'
    TODO = 'TODO'
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'
    ERROR = 'ERROR'
    SUCCESS = 'SUCCESS'
    FAIL = 'FAIL'

    @property
    def status(self) -> str: return self._obj.status

    @property
    def resolution(self) -> str: return self._obj.resolution

    @property
    def manual(self) -> str: return self._obj.manual

    @property
    def workflow(self) -> str: return self._obj.workflow

    @property
    def next(self) -> Optional[str]: return self._obj.next

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle): p.text(str(self) if not cycle else '...')

    def __init__(self, obj: ExpStructStatus): self._obj = obj

    def __str__(self): return str(self._obj)


class ExpStructAPI:

    @property
    def location_dir(self) -> str: return self._obj._location_dir

    @property
    def num(self) -> int: return self._obj._num

    @property
    def name(self) -> str:
        self._obj._update()
        return self._obj._name

    @property
    def descr(self) -> str:
        self._obj._update()
        return self._obj._descr

    @property
    def status(self) -> ExpStructStatusAPI:
        self._obj._update()
        return ExpStructStatusAPI(self._obj._status)

    @property
    def is_manual(self) -> bool:
        self._obj._update()
        return self._obj._is_manual

    def tree(self):
        self._obj._update()
        self._obj._tree()

    def info(self):
        self._obj._update()
        text = self._obj._info()
        print(text)

    def start(self):
        self._obj._update()
        self._obj._start()

    def set_manual_status(self, status: str, resolution: str) -> 'ExpStructAPI':
        self._obj._update()
        self._obj._set_manual_status(status, resolution)
        return self

    def delete_manual_status(self, need_confirm=True) -> Optional['ExpStructAPI']:
        self._obj._update()
        obj = self._obj._delete_manual_status(need_confirm)
        return None if obj is None else self

    def success(self, resolution: str) -> Optional['ExpAPI']:
        self._obj._update()
        self._obj._success(resolution)
        return self

    def fail(self, resolution: str) -> Optional['ExpAPI']:
        self._obj._update()
        self._obj._fail(resolution)
        return self

    def edit(self, name=None, descr=None):
        # Need to update parent (and all its children) to check other children on the same name:
        self._obj._update() if self._obj._parent is None else self._obj._parent._update()
        self._obj._edit(name, descr)

    def _update(self):
        self._obj._update()

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle): p.text(str(self) if not cycle else '...')

    def __init__(self, obj: ExpStruct):
        self._obj = obj

    def __str__(self):
        self._obj._update()
        return str(self._obj)


class ExpAPI(ExpStructAPI):

    @property
    def group(self) -> 'ExpGroupAPI':
        group = self._obj._parent
        group._update()
        return group.api

    @property
    def proj(self) -> 'ExpProjAPI':
        proj = self._obj._parent._parent
        proj._update()
        return proj.api

    @property
    def is_active(self) -> bool:
        self._obj._update()
        return self._obj._is_active

    @property
    def state(self) -> str:
        self._obj._update()
        return self._obj._state

    @property
    def result(self) -> Optional[Any]:
        self._obj._update()
        return self._obj._result

    @property
    def error(self) -> Optional[str]:
        self._obj._update()
        return self._obj._error

    @property
    def error_stack(self) -> Optional[str]:
        self._obj._update()
        return self._obj._error_stack

    def make_pipeline(self, run_func: Callable[..., Any],
                      params: dict, save_on_storage: bool = False) -> 'ExpAPI':
        self._obj._update()
        self._obj._make_pipeline(run_func, params, save_on_storage)
        return self

    def make_pipeline_with_checkpoints(self,
                                       run_func_with_mediator: Callable[[CheckpointsMediator, ...], Any],
                                       params: dict, save_on_storage: bool = False) -> 'ExpAPI':
        self._obj._update()
        self._obj._make_pipeline_with_checkpoints(run_func_with_mediator, params, save_on_storage)
        return self

    def get_pipeline_result(self) -> Optional[Any]:
        self._obj._update()
        return self._obj._get_pipeline_result()

    def destroy_pipeline(self, need_confirm=True) -> Optional['ExpAPI']:
        self._obj._update()
        obj = self._obj._destroy_pipeline(need_confirm)
        return None if obj is None else self

    # `self._obj._update()` isn't needed
    def get_checkpoints_mediator(self): return self._obj._get_checkpoints_mediator()

    def delete_checkpoints(self, need_confirm=True,
                           delete_custom_paths=False) -> Optional['ExpAPI']:
        self._obj._update()
        obj = self._obj._delete_checkpoints(need_confirm, delete_custom_paths)
        return None if obj is None else self

    def start(self):
        self._obj._update()
        self._obj._start()
        return self

    def set_manual_result(self, result) -> 'ExpAPI':
        self._obj._update()
        obj = self._obj._set_manual_result(result)
        return None if obj is None else self

    def delete_manual_result(self, need_confirm=True) -> Optional['ExpAPI']:
        self._obj._update()
        obj = self._obj._delete_manual_result(need_confirm)
        return None if obj is None else self

    def get_manual_result(self) -> Optional[Any]:
        self._obj._update()
        return self._obj._get_manual_result()

    def clear(self, need_confirm=True) -> Optional['Exp']:
        self._obj._update()
        obj = self._obj._clear(need_confirm)
        return None if obj is None else self


class ExpStructBoxAPI(ExpStructAPI):

    @property
    def num_children(self) -> int:
        self._obj._update()
        return self._obj._num_children


class ExpGroupAPI(ExpStructBoxAPI):

    @property
    def proj(self) -> 'ExpProjAPI':
        proj = self._obj._parent
        proj._update()
        return proj.api

    def has_exp(self, num_or_name) -> bool:
        self._obj._update()
        return self._obj._has_exp(num_or_name)

    def make_exp(self, name, descr, num=None) -> ExpAPI:
        self._obj._update()
        exp = self._obj._make_exp(name, descr, num)
        return exp.api

    def destroy_exp(self, num_or_name, need_confirm=True):
        self._obj._update()
        self._obj._destroy_exp(num_or_name, need_confirm)

    def exp(self, num_or_name) -> ExpAPI:
        self._obj._update()
        exp = self._obj._exp(num_or_name)
        return exp.api

    def exps(self) -> [ExpAPI]:
        self._obj._update()
        exps = self._obj._exps()
        return _get_exps_apis(exps)

    def filter_exps(self, active=None, manual=None) -> [ExpAPI]:
        self._obj._update()
        exps = self._obj._filter_exps(active, manual)
        return _get_exps_apis(exps)

    def get_exp_for_start(self) -> Optional[ExpAPI]:
        self._obj._update()
        exp = self._obj._get_exp_for_start()
        return None if exp is None else exp.api

    def start(self, exp_num_or_name=None, autostart_next=False):
        self._obj._update()
        self._obj._start(exp_num_or_name, autostart_next)

    def change_exp_num(self, num_or_name: int | str, new_num: int):
        self._obj._update()
        self._obj._change_exp_num(num_or_name, new_num)


class ExpProjAPI(ExpStructBoxAPI):

    @property
    def num(self) -> int:
        raise NotImplementedXManError(f"`num` property isn't supported for a project!")

    def has_group(self, num_or_name) -> bool:
        self._obj._update()
        return self._obj._has_group(num_or_name)

    def make_group(self, name, descr, num=None) -> ExpGroupAPI:
        self._obj._update()
        group = self._obj._make_group(name, descr, num)
        return group.api

    def destroy_group(self, num_or_name, need_confirm=True):
        self._obj._update()
        self._obj._destroy_group(num_or_name, need_confirm)

    def group(self, num_or_name) -> ExpGroupAPI:
        self._obj._update()
        group = self._obj._group(num_or_name)
        return group.api

    def groups(self) -> [ExpGroupAPI]:
        self._obj._update()
        groups = self._obj._groups()
        return _get_groups_apis(groups)

    def has_exp(self, group_num_or_name: int | str, exp_num_or_name: int | str) -> bool:
        self._obj._update()
        return self._obj._has_exp(group_num_or_name, exp_num_or_name)

    def make_exp(self, group_num_or_name, name, descr, num=None) -> ExpAPI:
        self._obj._update()
        exp = self._obj._make_exp(group_num_or_name, name, descr, num)
        return exp.api

    def destroy_exp(self, group_num_or_name: int | str, exp_num_or_name: int | str,
                    need_confirm=True):
        self._obj._update()
        self._obj._destroy_exp(group_num_or_name, exp_num_or_name, need_confirm)

    def exp(self, group_num_or_name: int | str, exp_num_or_name: int | str) -> ExpAPI:
        self._obj._update()
        exp = self._obj._exp(group_num_or_name, exp_num_or_name)
        return exp.api

    def exps(self, group_num_or_name=None) -> [ExpAPI]:
        self._obj._update()
        exps = self._obj._exps(group_num_or_name)
        return _get_exps_apis(exps)

    def filter_exps(self, active=None, manual=None) -> [ExpAPI]:
        self._obj._update()
        exps = self._obj._filter_exps(active, manual)
        return _get_exps_apis(exps)

    def start(self, group_num_or_name: Optional[int | str] = None,
              exp_num_or_name: Optional[int | str] = None, autostart_next=False):
        self._obj._update()
        self._obj._start(group_num_or_name, exp_num_or_name, autostart_next)

    def change_group_num(self, num_or_name: int | str, new_num: int):
        self._obj._update()
        self._obj._change_group_num(num_or_name, new_num)

    def move_exp(self, group_num_or_name, exp_num_or_name, new_group_num_or_name, new_exp_num):
        self._obj._update()
        self._obj._move_exp(group_num_or_name, exp_num_or_name, new_group_num_or_name, new_exp_num)


class XManAPI:

    @staticmethod
    def dir_tree(target_dir, files_limit=10, files_first=True, sort_numbers=True):
        tree.print_dir_tree(target_dir, files_limit, files_first, sort_numbers)

    @staticmethod
    def make_dir(dir_path): filesystem.make_dir(dir_path)

    @staticmethod
    def remove_dir(dir_path): filesystem.remove_dir(dir_path)

    @staticmethod
    def rename_or_move_dir(dir_path, new_path): filesystem.rename_or_move_dir(dir_path, new_path)

    @property
    def proj(self) -> ExpProjAPI:
        self.__check_proj()
        self.__proj._update()
        return self.__proj

    def make_proj(self, location_dir: str, name: str, descr: str) -> ExpProjAPI:
        proj = maker._make_proj(location_dir, name, descr)
        self.__destroy_old_proj()
        self.__proj = proj.api
        return self.__proj

    def load_proj(self, location_dir: str) -> ExpProjAPI:
        proj = maker._recreate_proj(location_dir)
        self.__destroy_old_proj()
        self.__proj = proj.api
        return self.__proj

    def info(self):
        self.__check_proj()
        self.__proj.info()

    def make_group(self, name, descr, num=None):
        self.__check_proj()
        return self.__proj.make_group(name, descr, num)

    def destroy_group(self, num_or_name, need_confirm=True):
        self.__check_proj()
        return self.__proj.destroy_group(num_or_name, need_confirm)

    def group(self, num_or_name):
        self.__check_proj()
        return self.__proj.group(num_or_name)

    def groups(self):
        self.__check_proj()
        return self.__proj.groups()

    def make_exp(self, group_num_or_name, name, descr, num=None):
        self.__check_proj()
        return self.__proj.make_exp(group_num_or_name, name, descr, num)

    def destroy_exp(self, group_num_or_name: int | str, exp_num_or_name: int | str,
                    need_confirm=True):
        self.__check_proj()
        return self.__proj.destroy_exp(group_num_or_name, exp_num_or_name, need_confirm)

    def exp(self, group_num_or_name: int | str, exp_num_or_name: int | str):
        self.__check_proj()
        return self.__proj.exp(group_num_or_name, exp_num_or_name)

    def exps(self, group_num_or_name=None):
        self.__check_proj()
        return self.__proj.exps(group_num_or_name)

    def filter_exps(self, active=None, manual=None) -> [ExpAPI]:
        self.__check_proj()
        return self.__proj.filter_exps(active, manual)

    def start(self, group_num_or_name: Optional[int | str] = None,
              exp_num_or_name: Optional[int | str] = None, autostart_next=False):
        self.__check_proj()
        self.__proj.start(group_num_or_name, exp_num_or_name, autostart_next)

    def __init__(self): self.__proj: ExpProjAPI = None

    def __check_proj(self):
        if self.__proj is None:
            raise IllegalOperationXManError(f"There's no project - use `xman.make_proj(...)` or "
                                            f"`xman.load_proj(...)` first!")

    def __destroy_old_proj(self):
        if self.__proj is not None:
            self.__proj._obj._destroy()
            self.__proj = None
