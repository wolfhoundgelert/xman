import os
import shutil
from typing import Any, Optional, Callable

from . import tree, maker, confirm
from .error import NotImplementedXManError, IllegalOperationXManError
from .pipeline import CheckpointsMediator
from .proj import ExpProj
from .exp import Exp
from .group import ExpGroup
from .struct import ExpStructStatus, ExpStruct
from .structbox import ExpStructBox


def _get_exp_api(exp):
    if exp._api is None:
        ExpAPI(exp)
    return exp._api


def _get_exps_apis(exps): return [_get_exp_api(exp) for exp in exps]


def _get_group_api(group):
    if group._api is None:
        ExpGroupAPI(group)
    return group._api


def _get_groups_apis(groups): return [_get_group_api(group) for group in groups]


class ExpStructStatusAPI:

    EMPTY = 'EMPTY'
    TODO = 'TODO'
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'
    ERROR = 'ERROR'
    SUCCESS = 'SUCCESS'
    FAIL = 'FAIL'

    @property
    def status(self) -> str: return self.__obj.status

    @property
    def resolution(self) -> str: return self.__obj.resolution

    @property
    def manual(self) -> str: return self.__obj.manual

    @property
    def workflow(self) -> str: return self.__obj.workflow

    @property
    def next(self) -> Optional[str]: return self.__obj.next

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle): p.text(str(self) if not cycle else '...')

    def __init__(self, obj: ExpStructStatus): self.__obj = obj

    def __str__(self): return str(self.__obj)


class ExpStructAPI:

    @property
    def location_dir(self) -> str: return self.__obj._location_dir

    @property
    def num(self) -> int: return self.__obj._num

    @property
    def name(self) -> str:
        self.__obj._update()
        return self.__obj._name

    @property
    def descr(self) -> str:
        self.__obj._update()
        return self.__obj._descr

    @property
    def status(self) -> ExpStructStatusAPI:
        self.__obj._update()
        return ExpStructStatusAPI(self.__obj._status)

    @property
    def is_manual(self) -> bool:
        self.__obj._update()
        return self.__obj._is_manual

    def tree(self):
        self.__obj._update()
        self.__obj._tree()

    def info(self):
        self.__obj._update()
        text = self.__obj._info()
        print(text)

    def start(self):
        self.__obj._update()
        self.__obj._start()

    def set_manual_status(self, status: str, resolution: str) -> 'ExpStructAPI':
        self.__obj._update()
        self.__obj._set_manual_status(status, resolution)
        return self

    def delete_manual_status(self, need_confirm=True) -> Optional['ExpStructAPI']:
        self.__obj._update()
        obj = self.__obj._delete_manual_status(need_confirm)
        return None if obj is None else self

    def success(self, resolution: str) -> Optional['ExpAPI']:
        self.__obj._update()
        self.__obj._success(resolution)
        return self

    def fail(self, resolution: str) -> Optional['ExpAPI']:
        self.__obj._update()
        self.__obj._fail(resolution)
        return self

    def edit(self, name=None, descr=None):
        # Need to update parent (and all its children) to check other children on the same name:
        self.__obj._update() if self.__obj._parent is None else self.__obj._parent._update()
        self.__obj._edit(name, descr)

    def _update(self):
        self.__obj._update()

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle): p.text(str(self) if not cycle else '...')

    def __init__(self, obj: ExpStruct):
        self.__obj = obj
        obj._api = self

    def __str__(self):
        self.__obj._update()
        return str(self.__obj)


class ExpAPI(ExpStructAPI):

    @property
    def state(self) -> str:
        self.__obj._update()
        return self.__obj._state

    @property
    def result(self) -> Optional[Any]:
        self.__obj._update()
        return self.__obj._result

    @property
    def error(self) -> Optional[str]:
        self.__obj._update()
        return self.__obj._error

    @property
    def error_stack(self) -> Optional[str]:
        self.__obj._update()
        return self.__obj._error_stack

    def make_pipeline(self, run_func: Callable[..., Any],
                      params: dict, save_on_storage: bool = False) -> 'ExpAPI':
        self.__obj._update()
        self.__obj._make_pipeline(run_func, params, save_on_storage)
        return self

    def make_pipeline_with_checkpoints(self,
                                       run_func_with_mediator: Callable[[CheckpointsMediator, ...], Any],
                                       params: dict, save_on_storage: bool = False) -> 'ExpAPI':
        self.__obj._update()
        self.__obj._make_pipeline_with_checkpoints(run_func_with_mediator, params, save_on_storage)
        return self

    def get_pipeline_result(self) -> Optional[Any]:
        self.__obj._update()
        return self.__obj._get_pipeline_result()

    def destroy_pipeline(self, need_confirm=True) -> Optional['ExpAPI']:
        self.__obj._update()
        obj = self.__obj._destroy_pipeline(need_confirm)
        return None if obj is None else self

    # `self.__obj._update()` isn't needed
    def get_checkpoints_mediator(self): return self.__obj._get_checkpoints_mediator()

    def delete_checkpoints(self, need_confirm=True,
                           delete_custom_paths=False) -> Optional['ExpAPI']:
        self.__obj._update()
        obj = self.__obj._delete_checkpoints(need_confirm, delete_custom_paths)
        return None if obj is None else self

    def start(self):
        self.__obj._update()
        self.__obj._start()
        return self

    def set_manual_result(self, result) -> 'ExpAPI':
        self.__obj._update()
        obj = self.__obj._set_manual_result(result)
        return None if obj is None else self

    def delete_manual_result(self, need_confirm=True) -> Optional['ExpAPI']:
        self.__obj._update()
        obj = self.__obj._delete_manual_result(need_confirm)
        return None if obj is None else self

    def get_manual_result(self) -> Optional[Any]:
        self.__obj._update()
        return self.__obj._get_manual_result()

    def clear(self, need_confirm=True) -> Optional['Exp']:
        self.__obj._update()
        obj = self.__obj._clear(need_confirm)
        return None if obj is None else self

    def __init__(self, obj: Exp):
        super().__init__(obj)
        self.__obj = obj


class ExpStructBoxAPI(ExpStructAPI):

    @property
    def num_children(self) -> int:
        self.__obj._update()
        return self.__obj._num_children

    def __init__(self, obj: ExpStructBox):
        super().__init__(obj)
        self.__obj = obj


class ExpGroupAPI(ExpStructBoxAPI):

    def has_exp(self, num_or_name) -> bool:
        self.__obj._update()
        return self.__obj._has_exp(num_or_name)

    def make_exp(self, name, descr, num=None) -> ExpAPI:
        self.__obj._update()
        exp = self.__obj._make_exp(name, descr, num)
        return _get_exp_api(exp)

    def destroy_exp(self, num_or_name, need_confirm=True):
        self.__obj._update()
        self.__obj._destroy_exp(num_or_name, need_confirm)

    def exp(self, num_or_name) -> ExpAPI:
        self.__obj._update()
        exp = self.__obj._exp(num_or_name)
        return _get_exp_api(exp)

    def exps(self) -> [ExpAPI]:
        self.__obj._update()
        exps = self.__obj._exps()
        return _get_exps_apis(exps)

    def get_exp_for_start(self) -> Optional[ExpAPI]:
        self.__obj._update()
        exp = self.__obj._get_exp_for_start()
        return None if exp is None else _get_exp_api(exp)

    def start(self, exp_num_or_name=None, autostart_next=False):
        self.__obj._update()
        self.__obj._start(exp_num_or_name, autostart_next)

    def change_exp_num(self, num_or_name):  # TODO Implement in ExpGroup
        self.__obj._update()
        self.__obj._change_exp_num(num_or_name)

    def __init__(self, obj: ExpGroup):
        super().__init__(obj)
        self.__obj = obj


class ExpProjAPI(ExpStructBoxAPI):

    @property
    def num(self) -> int:
        raise NotImplementedXManError(f"`num` property isn't supported for a project!")

    def has_group(self, num_or_name) -> bool:
        self.__obj._update()
        return self.__obj._has_group(num_or_name)

    def make_group(self, name, descr, num=None) -> ExpGroupAPI:
        self.__obj._update()
        group = self.__obj._make_group(name, descr, num)
        return _get_group_api(group)

    def destroy_group(self, num_or_name, need_confirm=True):
        self.__obj._update()
        self.__obj._destroy_group(num_or_name, need_confirm)

    def group(self, num_or_name) -> ExpGroupAPI:
        self.__obj._update()
        group = self.__obj._group(num_or_name)
        return _get_group_api(group)

    def groups(self) -> [ExpGroupAPI]:
        self.__obj._update()
        groups = self.__obj._groups()
        return _get_groups_apis(groups)

    def has_exp(self, group_num_or_name: int | str, exp_num_or_name: int | str) -> bool:
        self.__obj._update()
        return self.__obj._has_exp(group_num_or_name, exp_num_or_name)

    def make_exp(self, group_num_or_name, name, descr, num=None) -> ExpAPI:
        self.__obj._update()
        exp = self.__obj._make_exp(group_num_or_name, name, descr, num)
        return _get_exp_api(exp)

    def destroy_exp(self, group_num_or_name: int | str, exp_num_or_name: int | str,
                    need_confirm=True):
        self.__obj._update()
        self.__obj._destroy_exp(group_num_or_name, exp_num_or_name, need_confirm)

    def exp(self, group_num_or_name: int | str, exp_num_or_name: int | str) -> ExpAPI:
        self.__obj._update()
        exp = self.__obj._exp(group_num_or_name, exp_num_or_name)
        return _get_exp_api(exp)

    def exps(self, group_num_or_name=None) -> [ExpAPI]:
        self.__obj._update()
        exps = self.__obj._exps(group_num_or_name)
        return _get_exps_apis(exps)

    def start(self, group_num_or_name: Optional[int | str] = None,
              exp_num_or_name: Optional[int | str] = None, autostart_next=False):
        self.__obj._update()
        self.__obj._start(group_num_or_name, exp_num_or_name, autostart_next)

    # TODO Implement and use group_num_or_name, exp_num_or_name
    # def move_exp(self, dot_num, new_dot_num):
    #     self.__obj._update()
    #     self.__obj._move_exp(dot_num, new_dot_num)

    def _destroy(self):
        self.__obj._destroy()
        del self.__obj

    def __init__(self, obj: ExpProj):
        super().__init__(obj)
        self.__obj = obj


class XManAPI:

    @staticmethod
    def dir_tree(target_dir, files_limit=10, files_first=True, sort_numbers=True):
        tree.print_dir_tree(target_dir, files_limit, files_first, sort_numbers)

    @staticmethod
    def make_dir(dir_path): os.makedirs(dir_path, exist_ok=True)

    @staticmethod
    def remove_dir(dir_path):
        if len(os.listdir(dir_path)) > 0 and not confirm._request(
                True, f"ATTENTION! Dir `{dir_path}` isn't empty - proceed?"):
            return
        shutil.rmtree(dir_path, ignore_errors=True)

    __proj: ExpProjAPI = None

    @property
    def proj(self) -> ExpProjAPI:
        self.__check_proj()
        self.__proj._update()
        return self.__proj

    def make_proj(self, location_dir: str, name: str, descr: str):
        obj = maker._make_proj(location_dir, name, descr)
        return self.__make_proj_api(obj)

    def load_proj(self, location_dir: str):
        obj = maker._recreate_proj(location_dir)
        return self.__make_proj_api(obj)

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

    def start(self, group_num_or_name: Optional[int | str] = None,
              exp_num_or_name: Optional[int | str] = None, autostart_next=False):
        self.__check_proj()
        self.__proj.start(group_num_or_name, exp_num_or_name, autostart_next)

    def __make_proj_api(self, obj):
        if self.__proj is not None:
            self.__proj._destroy()
        self.__proj = ExpProjAPI(obj)
        return self.__proj

    def __check_proj(self):
        if self.__proj is None:
            raise IllegalOperationXManError(f"There's no project - use `xman.make_proj(...)` or "
                                            f"`xman.load_proj(...)` first!")
