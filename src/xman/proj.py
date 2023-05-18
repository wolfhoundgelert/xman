from typing import List

from . import filesystem
from .error import NothingToDoXManError, IllegalOperationXManError, NotExistsXManError, \
    AlreadyExistsXManError
from .structbox import ExpStructBox
from .group import ExpGroup
from .exp import Exp


class ExpProj(ExpStructBox):

    def has_group(self, num_or_name) -> bool: return self.has_child_with_num_or_name(num_or_name)

    def make_group(self, name, descr, num=None) -> ExpGroup:
        return self.make_child(name, descr, num)

    def delete_group(self, num_or_name, need_confirm=True):
        # TODO Refactor as ExpGroup and ExpProj _check_no_active_exps()
        group = self.group(num_or_name)
        actives = [exp for exp in group.exps() if exp.is_active]
        if len(actives):
            raise IllegalOperationXManError(f"The `{group}` has active experiment(s): {actives}!")
        self.delete_child(num_or_name, need_confirm)

    def change_group_num(self, num_or_name, new_num):
        # TODO check active experiments
        self._change_child_num(num_or_name, new_num)

    def group(self, num_or_name) -> ExpGroup: return self.get_child_by_num_or_name(num_or_name)

    def groups(self) -> List[ExpGroup]: return self.children

    def has_exp(self, group_num_or_name, exp_num_or_name) -> bool:
        return self.group(group_num_or_name).has_exp(exp_num_or_name)

    def make_exp(self, group_num_or_name, name, descr, num=None) -> Exp:
        return self.group(group_num_or_name).make_exp(name, descr, num)

    def delete_exp(self, group_num_or_name, exp_num_or_name, need_confirm=True):
        self.group(group_num_or_name).delete_exp(exp_num_or_name, need_confirm)

    def exp(self, group_num_or_name, exp_num_or_name) -> Exp:
        return self.group(group_num_or_name).exp(exp_num_or_name)

    def exps(self, group_num_or_name=None) -> List[Exp]:
        if group_num_or_name is not None:
            return self.group(group_num_or_name).exps()
        result = []
        for it in self.groups():
            result.extend(it.exps())
        return result

    # TODO Implement more global in `filter.py`
    def filter_exps(self, active=None, manual=None, ready_for_start=None) -> List[Exp]:
        # TODO active
        # TODO manual
        pass  # TODO

    def start(self, group_num_or_name=None, exp_num_or_name=None, autostart_next=False):
        exp = None
        if group_num_or_name is None and exp_num_or_name is None:
            for group in self.groups():
                exp = group.get_exp_for_start()
                if exp is not None:
                    break
            if exp is None:
                raise NothingToDoXManError(f"There's nothing to start in the `{self}`!")
        elif group_num_or_name is not None and exp_num_or_name is not None:
            exp = self.exp(group_num_or_name, exp_num_or_name)
            if not exp.is_ready_for_start:
                raise IllegalOperationXManError(f"Can't start the `{exp}` because of its status "
                                                f"`{exp.status}` and state `{exp.state}`!")
        elif group_num_or_name is not None and exp_num_or_name is None:
            group = self.group(group_num_or_name)
            exp = group.get_exp_for_start()
            if exp is None:
                raise NothingToDoXManError(f"There's nothing to start in the `{group}`!")
        elif group_num_or_name is None and exp_num_or_name is not None:
            for group in self.groups():
                if group.has_exp(exp_num_or_name):
                    e = group.exp(exp_num_or_name)
                    if e.is_ready_for_start:
                        exp = e
                        break
            if exp is None:
                raise NothingToDoXManError(f"There's no experiment with `num_or_name`=="
                                           f"`{exp_num_or_name}` to start in the `{self}`!")
        exp.start()
        if autostart_next:
            self.start(autostart_next=True)

    def move_exp(self, group_num_or_name, exp_num_or_name, new_group_num_or_name, new_exp_num):
        exp = self.exp(group_num_or_name, exp_num_or_name)
        exp._check_not_active()
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

    def update(self):
        if self.__updating:
            return
        self.__updating = True
        super().update()
        # Status should be updated at the end of the inherited updating hierarchy
        if type(self) == ExpProj:
            self._update_status()
        self.__updating = False

    def __init__(self, location_dir):
        from .api import ExpProjAPI
        self.__updating = False
        super().__init__(location_dir, None)
        self._api = ExpProjAPI(self)

    def __str__(self): return f"Proj [{self.status}] {self._data.name} - {self._data.descr}"
