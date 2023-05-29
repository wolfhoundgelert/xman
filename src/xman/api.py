from typing import Any, Optional, Callable, List

from . import tree, maker, filesystem
from .error import NotImplementedXManError, IllegalOperationXManError
from .group import ExpGroup
from .note import Note
from .pipeline import CheckpointsMediator
from .exp import Exp
from .proj import ExpProj
from .struct import ExpStructStatus, ExpStruct


def _get_apis_from_list(objs: List[Exp | ExpGroup]) -> List['ExpAPI | ExpGroupAPI']:
    return [x.api for x in objs]


class ExpStructAPI:

    @property
    def location_dir(self) -> str: return self._obj.location_dir

    @property
    def num(self) -> int: return self._obj.num

    @property
    def name(self) -> str:
        self._obj.update()
        return self._obj.name

    @property
    def descr(self) -> str:
        self._obj.update()
        return self._obj.descr

    @property
    def status(self) -> ExpStructStatus:
        self._obj.update()
        return self._obj.status

    @property
    def is_manual(self) -> bool:
        self._obj.update()
        return self._obj.is_manual

    @property
    def result_viewer(self) -> Callable[[Any], str]:
        self._obj.update()
        return self._obj.result_viewer

    @result_viewer.setter
    def result_viewer(self, value: Callable[[Any], str]):
        self._obj.update()
        self._obj.result_viewer = value

    @property
    def note(self) -> Note:
        # self._obj.update()  # No need to update
        return self._obj.note

    def tree(self, depth: int = None):
        self._obj.update()
        self._obj.tree(depth)

    def info(self):
        self._obj.update()
        text = self._obj.info()
        print(text)

    def update(self):
        self._obj.update()

    def set_manual_status(self, status: str, resolution: str) -> 'ExpStructAPI':
        self._obj.update()
        self._obj.set_manual_status(status, resolution)
        return self

    def delete_manual_status(self, need_confirm: bool = True) -> Optional['ExpStructAPI']:
        self._obj.update()
        obj = self._obj.delete_manual_status(need_confirm)
        return None if obj is None else self

    def success(self, resolution: str) -> Optional['ExpStructAPI']:
        self._obj.update()
        self._obj.success(resolution)
        return self

    def fail(self, resolution: str) -> Optional['ExpStructAPI']:
        self._obj.update()
        self._obj.fail(resolution)
        return self

    def edit(self, name: Optional[str] = None, descr: Optional[str] = None):
        # Need to update parent (and all its children) to check other children on the same name:
        self._obj.update() if self._obj.parent is None else self._obj.parent.update()
        self._obj.edit(name, descr)

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle): p.text(str(self) if not cycle else '...')

    def __init__(self, obj: ExpStruct): self._obj = obj  # for autocomplete

    def __str__(self):
        self._obj.update()
        return str(self._obj)


class ExpAPI(ExpStructAPI):

    @property
    def group(self) -> 'ExpGroupAPI':
        group = self._obj.group
        group.update()
        return group.api

    @property
    def proj(self) -> 'ExpProjAPI':
        proj = self._obj.proj
        proj.update()
        return proj.api

    @property
    def is_active(self) -> bool:
        self._obj.update()
        return self._obj.is_active

    @property
    def is_ready_for_start(self) -> bool:
        self._obj.update()
        return self._obj.is_ready_for_start

    @property
    def state(self) -> str:
        self._obj.update()
        return self._obj.state

    @property
    def result(self) -> Optional[Any]:
        self._obj.update()
        return self._obj.result

    @property
    def error(self) -> Optional[str]:
        self._obj.update()
        return self._obj.error

    @property
    def error_stack(self) -> Optional[str]:
        self._obj.update()
        return self._obj.error_stack

    @property
    def checkpoints_mediator(self) -> CheckpointsMediator:
        # self._obj.update()  # No need to update
        return self._obj.checkpoints_mediator

    def view_result(self) -> str:
        self._obj.update()
        text = self._obj.view
        print(text)

    def make_pipeline(self, run_func: Callable[..., Any],
                      params: dict, save_on_storage: bool = False) -> 'ExpAPI':
        self._obj.update()
        self._obj.make_pipeline(run_func, params, save_on_storage)
        return self

    def make_pipeline_with_checkpoints(self,
                               run_func_with_mediator: Callable[[CheckpointsMediator, ...], Any],
                               params: dict, save_on_storage: bool = False) -> 'ExpAPI':
        self._obj.update()
        self._obj.make_pipeline_with_checkpoints(run_func_with_mediator, params, save_on_storage)
        return self

    def get_pipeline_result(self) -> Optional[Any]:
        self._obj.update()
        return self._obj.get_pipeline_result()

    def delete_pipeline(self, need_confirm: bool = True) -> Optional['ExpAPI']:
        self._obj.update()
        obj = self._obj.delete_pipeline(need_confirm)
        return None if obj is None else self

    def delete_checkpoints(self, need_confirm: bool = True,
                           delete_custom_paths: bool = False) -> Optional['ExpAPI']:
        self._obj.update()
        obj = self._obj.delete_checkpoints(need_confirm, delete_custom_paths)
        return None if obj is None else self

    def start(self) -> 'ExpAPI':
        self._obj.update()
        self._obj.start()
        return self

    def set_manual_result(self, result: Any) -> 'ExpAPI':
        self._obj.update()
        obj = self._obj.set_manual_result(result)
        return None if obj is None else self

    def delete_manual_result(self, need_confirm: bool = True) -> Optional['ExpAPI']:
        self._obj.update()
        obj = self._obj.delete_manual_result(need_confirm)
        return None if obj is None else self

    def get_manual_result(self) -> Optional[Any]:
        self._obj.update()
        return self._obj.get_manual_result()

    def delete_all_manual(self, need_confirm: bool = True) -> Optional['ExpAPI']:
        self._obj.update()
        obj = self._obj.delete_all_manual(need_confirm)
        return None if obj is None else self

    def clear(self, need_confirm: bool = True) -> Optional['ExpAPI']:
        self._obj.update()
        obj = self._obj.clear(need_confirm)
        return None if obj is None else self

    def __init__(self, obj: Exp): self._obj = obj  # for autocomplete


class ExpGroupAPI(ExpStructAPI):

    @property
    def proj(self) -> 'ExpProjAPI':
        proj = self._obj.parent
        proj.update()
        return proj.api

    def has_exp(self, num_or_name: int | str) -> bool:
        self._obj.update()
        return self._obj.has_exp(num_or_name)

    def exp(self, num_or_name: int | str) -> ExpAPI:
        self._obj.update()
        exp = self._obj.exp(num_or_name)
        return exp.api

    def make_exp(self, name: str, descr: str, num: Optional[int] = None) -> ExpAPI:
        self._obj.update()
        exp = self._obj.make_exp(name, descr, num)
        return exp.api

    def delete_exp(self, num_or_name: int | str, need_confirm: bool = True) -> bool:
        self._obj.update()
        return self._obj.delete_exp(num_or_name, need_confirm)

    def exps(self) -> List[ExpAPI]:
        self._obj.update()
        exps = self._obj.exps()
        return _get_apis_from_list(exps)

    def num_exps(self) -> int:
        self._obj.update()
        return self._obj.num_exps()

    def exps_nums(self) -> List[int]:
        self._obj.update()
        return self._obj.exps_nums()

    def exps_names(self) -> List[str]:
        self._obj.update()
        return self._obj.exps_names()

    def change_exp_num(self, num_or_name: int | str, new_num: int):
        self._obj.update()
        self._obj.change_exp_num(num_or_name, new_num)

    def filter_exps(self,
                    mode: str = 'AND',
                    custom_filter: Optional[Callable[[Exp], bool]] = None,
                    is_active: Optional[bool] = None,
                    is_manual: Optional[bool] = None,
                    is_ready_for_start: Optional[bool] = None,
                    status_or_list: Optional[str | List[str]] = None,
                    not_status_or_list: Optional[str | List[str]] = None,
                    ) -> List[ExpAPI]:
        self._obj.update()
        exps = self._obj.filter_exps(mode, custom_filter, is_active, is_manual, is_ready_for_start,
                                     status_or_list, not_status_or_list)
        return _get_apis_from_list(exps)

    def get_exp_for_start(self) -> Optional[ExpAPI]:
        self._obj.update()
        exp = self._obj.get_exp_for_start()
        return None if exp is None else exp.api

    def start(self, exp_num_or_name: Optional[int | str] = None, autostart_next: bool = False):
        self._obj.update()
        self._obj.start(exp_num_or_name, autostart_next)

    def __init__(self, obj: ExpGroup): self._obj = obj  # for autocomplete


class ExpProjAPI(ExpStructAPI):

    @property
    def num(self) -> int:
        raise NotImplementedXManError(f"`num` property isn't supported for a project!")

    def has_group(self, num_or_name: int | str) -> bool:
        self._obj.update()
        return self._obj.has_group(num_or_name)

    def group(self, num_or_name: int | str) -> ExpGroupAPI:
        self._obj.update()
        group = self._obj.group(num_or_name)
        return group.api

    def make_group(self, name: str, descr: str, num: Optional[int] = None) -> ExpGroupAPI:
        self._obj.update()
        group = self._obj.make_group(name, descr, num)
        return group.api

    def delete_group(self, num_or_name: int | str, need_confirm: bool = True) -> bool:
        self._obj.update()
        return self._obj.delete_group(num_or_name, need_confirm)

    def groups(self) -> List[ExpGroupAPI]:
        self._obj.update()
        groups = self._obj.groups()
        return _get_apis_from_list(groups)

    def num_groups(self) -> int:
        self._obj.update()
        return self._obj.num_groups()

    def groups_nums(self) -> List[int]:
        self._obj.update()
        return self._obj.groups_nums()

    def groups_names(self) -> List[str]:
        self._obj.update()
        return self._obj.groups_names()

    def change_group_num(self, num_or_name: int | str, new_num: int):
        self._obj.update()
        self._obj.change_group_num(num_or_name, new_num)

    def filter_groups(self,
                      mode: str = 'AND',
                      custom_filter: Optional[Callable[[ExpGroup], bool]] = None,
                      status_or_list: Optional[str | List[str]] = None,
                      not_status_or_list: Optional[str | List[str]] = None,
                      ) -> List[ExpGroupAPI]:
        self._obj.update()
        groups = self._obj.filter_groups(mode, custom_filter, status_or_list, not_status_or_list)
        return _get_apis_from_list(groups)

    def has_exp(self, group_num_or_name: int | str, exp_num_or_name: int | str) -> bool:
        self._obj.update()
        return self._obj.has_exp(group_num_or_name, exp_num_or_name)

    def exp(self, group_num_or_name: int | str, exp_num_or_name: int | str) -> ExpAPI:
        self._obj.update()
        exp = self._obj.exp(group_num_or_name, exp_num_or_name)
        return exp.api

    def make_exp(self, group_num_or_name: int | str, name: str, descr: str,
                 num: Optional[int] = None) -> ExpAPI:
        self._obj.update()
        exp = self._obj.make_exp(group_num_or_name, name, descr, num)
        return exp.api

    def delete_exp(self, group_num_or_name: int | str, exp_num_or_name: int | str,
                   need_confirm: bool = True) -> bool:
        self._obj.update()
        return self._obj.delete_exp(group_num_or_name, exp_num_or_name, need_confirm)

    def exps(self, group_num_or_name: Optional[int | str] = None) -> List[ExpAPI]:
        self._obj.update()
        exps = self._obj.exps(group_num_or_name)
        return _get_apis_from_list(exps)

    def num_exps(self, group_num_or_name: Optional[int | str] = None) -> int:
        self._obj.update()
        return self._obj.num_exps(group_num_or_name)

    def exps_nums(self, group_num_or_name: Optional[int | str] = None) -> List[int]:
        self._obj.update()
        return self._obj.exps_nums(group_num_or_name)

    def exps_names(self, group_num_or_name: Optional[int | str] = None) -> List[str]:
        self._obj.update()
        return self._obj.exps_names(group_num_or_name)

    def filter_exps(self,
                    group_num_or_name: Optional[int | str] = None,
                    mode: str = 'AND',
                    custom_filter: Optional[Callable[[Exp], bool]] = None,
                    is_active: Optional[bool] = None,
                    is_manual: Optional[bool] = None,
                    is_ready_for_start: Optional[bool] = None,
                    status_or_list: Optional[str | List[str]] = None,
                    not_status_or_list: Optional[str | List[str]] = None,
                    ) -> List[ExpAPI]:
        self._obj.update()
        exps = self._obj.filter_exps(group_num_or_name, mode, custom_filter, is_active, is_manual,
                                     is_ready_for_start, status_or_list, not_status_or_list)
        return _get_apis_from_list(exps)

    def get_exp_for_start(self, group_num_or_name: Optional[int | str] = None) -> Optional[ExpAPI]:
        self._obj.update()
        exp = self._obj.get_exp_for_start(group_num_or_name)
        return None if exp is None else exp.api

    def start(self, group_num_or_name: Optional[int | str] = None,
              exp_num_or_name: Optional[int | str] = None, autostart_next: bool = False):
        self._obj.update()
        self._obj.start(group_num_or_name, exp_num_or_name, autostart_next)

    def move_exp(self, group_num_or_name: int | str, exp_num_or_name: int | str,
                 new_group_num_or_name: int | str, new_exp_num: int):
        self._obj.update()
        self._obj.move_exp(group_num_or_name, exp_num_or_name, new_group_num_or_name, new_exp_num)

    def __init__(self, obj: ExpProj): self._obj = obj  # for autocomplete


class XManAPI:

    @staticmethod
    def dir_tree(target_dir: str, depth: int = 0, files_limit: int = 10,
                 files_first: bool = True, sort_numbers: bool = True):
        tree.print_dir_tree(target_dir, depth, files_limit, files_first, sort_numbers)

    @staticmethod
    def make_dir(dir_path: str, exist_ok: bool = True): filesystem.make_dir(dir_path, exist_ok)

    @staticmethod
    def delete_dir(dir_path: str, need_confirm: bool = True) -> bool:
        return filesystem.delete_dir(dir_path, need_confirm)

    @staticmethod
    def rename_or_move_dir(dir_path: str, new_path: str):
        filesystem.rename_or_move_dir(dir_path, new_path)

    @property
    def location_dir(self) -> str:
        self.__check_proj()
        return self.__proj.location_dir

    @property
    def proj(self) -> ExpProjAPI:
        self.__check_proj()
        self.__proj.update()
        return self.__proj

    def make_proj(self, location_dir: str, name: str, descr: str) -> ExpProjAPI:
        self.__destroy_old_proj()
        proj = maker.make_proj(location_dir, name, descr)
        self.__proj = proj.api
        return self.__proj

    def load_proj(self, location_dir: str) -> ExpProjAPI:
        self.__destroy_old_proj()
        proj = maker.recreate_proj(location_dir)
        self.__proj = proj.api
        return self.__proj

    def reload(self):
        self.__check_proj()
        self.load_proj(self.__proj.location_dir)

    def info(self):
        self.__check_proj()
        self.__proj.info()

    def update(self):
        self.__check_proj()
        self.__proj.update()

    def has_group(self, num_or_name: int | str) -> bool:
        self.__check_proj()
        return self.__proj.has_group(num_or_name)

    def group(self, num_or_name: int | str) -> ExpGroupAPI:
        self.__check_proj()
        return self.__proj.group(num_or_name)

    def make_group(self, name: str, descr: str, num: Optional[int] = None) -> ExpGroupAPI:
        self.__check_proj()
        return self.__proj.make_group(name, descr, num)

    def delete_group(self, num_or_name: int | str, need_confirm: bool = True) -> bool:
        self.__check_proj()
        return self.__proj.delete_group(num_or_name, need_confirm)

    def groups(self) -> List[ExpGroupAPI]:
        self.__check_proj()
        return self.__proj.groups()

    def filter_groups(self,
                      mode: str = 'AND',
                      custom_filter: Optional[Callable[[ExpGroup], bool]] = None,
                      status_or_list: Optional[str | List[str]] = None,
                      not_status_or_list: Optional[str | List[str]] = None,
                      ) -> List[ExpGroupAPI]:
        self.__check_proj()
        return self.__proj.filter_groups(mode, custom_filter, status_or_list, not_status_or_list)

    def has_exp(self, group_num_or_name: int | str, exp_num_or_name: int | str) -> bool:
        self.__check_proj()
        return self.__proj.has_exp(group_num_or_name, exp_num_or_name)

    def exp(self, group_num_or_name: int | str, exp_num_or_name: int | str) -> ExpAPI:
        self.__check_proj()
        return self.__proj.exp(group_num_or_name, exp_num_or_name)

    def make_exp(self, group_num_or_name: int | str, name: str, descr: str,
                 num: Optional[int] = None) -> ExpAPI:
        self.__check_proj()
        return self.__proj.make_exp(group_num_or_name, name, descr, num)

    def delete_exp(self, group_num_or_name: int | str, exp_num_or_name: int | str,
                   need_confirm: bool = True) -> bool:
        self.__check_proj()
        return self.__proj.delete_exp(group_num_or_name, exp_num_or_name, need_confirm)

    def exps(self, group_num_or_name: Optional[int | str] = None) -> List[ExpAPI]:
        self.__check_proj()
        return self.__proj.exps(group_num_or_name)

    def filter_exps(self,
                    group_num_or_name: Optional[int | str] = None,
                    mode: str = 'AND',
                    custom_filter: Optional[Callable[[Exp], bool]] = None,
                    is_active: Optional[bool] = None,
                    is_manual: Optional[bool] = None,
                    is_ready_for_start: Optional[bool] = None,
                    status_or_list: Optional[str | List[str]] = None,
                    not_status_or_list: Optional[str | List[str]] = None,
                    ) -> List[ExpAPI]:
        self.__check_proj()
        return self.__proj.filter_exps(group_num_or_name, mode, custom_filter, is_active, is_manual,
                                       is_ready_for_start, status_or_list, not_status_or_list)

    def get_exp_for_start(self, group_num_or_name: Optional[int | str] = None) -> Optional[ExpAPI]:
        self.__check_proj()
        return self.__proj.get_exp_for_start(group_num_or_name)

    def start(self, group_num_or_name: Optional[int | str] = None,
              exp_num_or_name: Optional[int | str] = None, autostart_next: bool = False):
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
