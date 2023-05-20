from typing import List, Optional, Callable

from . import filesystem, filter
from .error import NothingToDoXManError, NotExistsXManError, AlreadyExistsXManError, \
    ArgumentsXManError
from .structbox import ExpStructBox
from .group import ExpGroup
from .exp import Exp


class ExpProj(ExpStructBox):

    def update(self):
        if self.__updating:
            return
        self.__updating = True
        super().update()
        # Status should be updated at the end of the inherited updating hierarchy
        if type(self) == ExpProj:
            self._update_status()
        self.__updating = False

    def has_group(self, num_or_name) -> bool: return self.has_child(num_or_name)

    def group(self, num_or_name) -> ExpGroup: return self.child(num_or_name)

    def make_group(self, name, descr, num=None) -> ExpGroup:
        return self.make_child(name, descr, num)

    def delete_group(self, num_or_name, need_confirm=True) -> bool:
        self.group(num_or_name)._check_has_no_active_exps()
        return self.delete_child(num_or_name, need_confirm)

    def groups(self) -> List[ExpGroup]: return self.children()

    def num_groups(self) -> int: return self.num_children()

    def groups_nums(self) -> List[int]: return self.children_nums()

    def groups_names(self) -> List[str]: return self.children_names()

    def change_group_num(self, num_or_name, new_num):
        self.group(num_or_name)._check_has_no_active_exps()
        self.change_child_num(num_or_name, new_num)

    def filter_groups(self,
                      mode: str = 'AND',
                      custom_filter: Callable[[ExpGroup], bool] = None,
                      status_or_list: str | List[str] = None,
                      not_status_or_list: str | List[str] = None,
                      ) -> List[ExpGroup]:
        return filter.groups(self.groups(), mode, custom_filter, status_or_list, not_status_or_list)

    def has_exp(self, group_num_or_name, exp_num_or_name) -> bool:
        return self.group(group_num_or_name).has_exp(exp_num_or_name)

    def exp(self, group_num_or_name, exp_num_or_name) -> Exp:
        return self.group(group_num_or_name).exp(exp_num_or_name)

    def make_exp(self, group_num_or_name, name, descr, num=None) -> Exp:
        return self.group(group_num_or_name).make_exp(name, descr, num)

    def delete_exp(self, group_num_or_name, exp_num_or_name, need_confirm=True) -> bool:
        return self.group(group_num_or_name).delete_exp(exp_num_or_name, need_confirm)

    def exps(self, group_num_or_name=None) -> List[Exp]:
        if group_num_or_name is not None:
            return self.group(group_num_or_name).exps()
        result = []
        for it in self.groups():
            result.extend(it.exps())
        return result

    def num_exps(self, group_num_or_name=None) -> int:
        if group_num_or_name is not None:
            return self.group(group_num_or_name).num_exps()
        return len(self.exps())

    def exps_nums(self, group_num_or_name=None) -> List[int]:
        if group_num_or_name is not None:
            return self.group(group_num_or_name).exps_nums()
        return [x.num for x in self.exps()]

    def exps_names(self, group_num_or_name=None) -> List[str]:
        if group_num_or_name is not None:
            return self.group(group_num_or_name).exps_names()
        return [x.name for x in self.exps()]

    def filter_exps(self,
                    group_num_or_name: int | str = None,
                    mode: str = 'AND',
                    custom_filter: Callable[[Exp], bool] = None,
                    is_active: bool = None,
                    is_manual: bool = None,
                    is_ready_for_start: bool = None,
                    status_or_list: str | List[str] = None,
                    not_status_or_list: str | List[str] = None,
                    ) -> List[Exp]:
        if group_num_or_name is not None:
            return self.group(group_num_or_name).filter_exps(mode, custom_filter, is_active,
                                is_manual, is_ready_for_start, status_or_list, not_status_or_list)
        return filter.exps(self.exps(), mode, custom_filter, is_active, is_manual,
                           is_ready_for_start, status_or_list, not_status_or_list)

    def get_exp_for_start(self, group_num_or_name=None) -> Optional[Exp]:
        if group_num_or_name is not None:
            return self.group(group_num_or_name).get_exp_for_start()
        ready_list = filter.exps(self.exps(), is_ready_for_start=True)
        return ready_list[0] if len(ready_list) else None

    def start(self, group_num_or_name=None, exp_num_or_name=None, autostart_next=False):
        exp = None
        if group_num_or_name is None and exp_num_or_name is None:
            exp = self.get_exp_for_start()
        elif group_num_or_name is None and exp_num_or_name is not None:
            raise ArgumentsXManError(f"Need to specify `group_num_or_name` if `exp_num_or_name` is "
                                     f"specified!")
        elif group_num_or_name is not None and exp_num_or_name is None:
            exp = self.get_exp_for_start(group_num_or_name)
        elif group_num_or_name is not None and exp_num_or_name is not None:
            exp = self.exp(group_num_or_name, exp_num_or_name)
        if exp is None:
            raise NothingToDoXManError(f"There's nothing to start!")
        exp.start()
        if autostart_next:
            self.start(autostart_next=True)

    def move_exp(self, group_num_or_name, exp_num_or_name, new_group_num_or_name, new_exp_num):
        exp = self.exp(group_num_or_name, exp_num_or_name)
        exp._check_is_not_active()
        group = self.group(group_num_or_name)
        if not self.has_group(new_group_num_or_name):
            raise NotExistsXManError(f"There's no group with number or name "
                                     f"`{new_group_num_or_name}`!")
        new_group = self.group(new_group_num_or_name)
        if self.has_exp(new_group_num_or_name, new_exp_num):
            raise AlreadyExistsXManError(f"Can't move the experiment because another experiment"
                                    f"already exist in the group number `{new_group_num_or_name}`!")
        dir_path = exp.location_dir
        new_path = filesystem.change_group_num_in_path(dir_path, new_group.num)
        new_path = filesystem.change_exp_num_in_path(new_path, new_exp_num)
        filesystem.rename_or_move_dir(dir_path, new_path)
        group._remove_child(exp)
        # Also changes `num` as it's processing from the path:
        exp._change_location_dir(new_path)
        new_group._add_child(exp)

    def __init__(self, location_dir):
        from .api import ExpProjAPI
        self.__updating = False
        super().__init__(location_dir, None)
        self._api = ExpProjAPI(self)

    def __str__(self): return f"Proj [{self.status}] {self._data.name} - {self._data.descr}"
