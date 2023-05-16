from .error import NothingToDoXManError, IllegalOperationXManError
from .structbox import ExpStructBox
from .group import ExpGroup
from .exp import Exp


class ExpProj(ExpStructBox):

    def _has_group(self, num_or_name): return self._has_child_num_or_name(num_or_name)

    def _make_group(self, name, descr, num=None) -> ExpGroup:
        return self._make_child(name, descr, num)

    def _destroy_group(self, num_or_name, need_confirm=True):
        # TODO check hasn't active experiments
        self._destroy_child(num_or_name, need_confirm)

    def _group(self, num_or_name) -> ExpGroup: return self._get_child_by_num_or_name(num_or_name)

    def _groups(self) -> [ExpGroup]: return self._children()

    def _has_exp(self, group_num_or_name, exp_num_or_name) -> bool:
        return self._group(group_num_or_name)._has_exp(exp_num_or_name)

    def _make_exp(self, group_num_or_name, name, descr, num=None) -> Exp:
        group = self._group(group_num_or_name)
        exp = group._make_exp(name, descr, num)
        return exp
        self._has_exp()

    def _destroy_exp(self, group_num_or_name, exp_num_or_name, need_confirm=True):
        self._group(group_num_or_name)._destroy_exp(exp_num_or_name, need_confirm)

    def _exp(self, group_num_or_name, exp_num_or_name) -> Exp:
        return self._group(group_num_or_name)._exp(exp_num_or_name)

    def _exps(self, group_num_or_name=None) -> [Exp]:
        if group_num_or_name is not None:
            return self._group(group_num_or_name)._exps()
        result = []
        for it in self._groups():
            result.extend(it.exps())
        return result

    def _start(self, group_num_or_name=None, exp_num_or_name=None, autostart_next=False):
        exp = None
        if group_num_or_name is None and exp_num_or_name is None:
            for group in self._groups():
                exp = group._get_exp_for_start()
                if exp is not None:
                    break
            if exp is None:
                raise NothingToDoXManError(f"There's nothing to start in the `{self}`!")
        elif group_num_or_name is not None and exp_num_or_name is not None:
            exp = self._exp(group_num_or_name, exp_num_or_name)
            if not exp._is_ready_for_start():
                raise IllegalOperationXManError(f"Can't start the `{exp}` because of its status "
                                                f"`{exp._status}` and state `{exp._state}`!")
        elif group_num_or_name is not None and exp_num_or_name is None:
            group = self._group(group_num_or_name)
            exp = group._get_exp_for_start()
            if exp is None:
                raise NothingToDoXManError(f"There's nothing to start in the `{group}`!")
        elif group_num_or_name is None and exp_num_or_name is not None:
            for group in self._groups():
                if group._has_exp(exp_num_or_name):
                    e = group._exp(exp_num_or_name)
                    if e._is_ready_for_start():
                        exp = e
                        break
            if exp is None:
                raise NothingToDoXManError(f"There's no experiment with `num_or_name`=="
                                           f"`{exp_num_or_name}` to start in the `{self}`!")
        exp._start()
        if autostart_next:
            self._start(autostart_next=True)

    # TODO def _move_exp(self, dot_num, new_dot_num):

    def _update(self):
        if self.__updating:
            return
        self.__updating = True
        super()._update()
        # Status should be updated at the end of the inherited updating hierarchy
        if type(self) == ExpProj:
            self._update_status()
        self.__updating = False

    def __init__(self, location_dir):
        self.__updating = False
        super().__init__(location_dir, None)

    def __str__(self): return f"Proj [{self._status}] {self._data.name} - {self._data.descr}"
