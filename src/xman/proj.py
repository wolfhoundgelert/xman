from .error import NothingToDoXManError
from .structbox import ExpStructBox
from .group import ExpGroup
from .exp import Exp
from . import util


class ExpProj(ExpStructBox):

    def has_group(self, num_or_name):
        self._update()
        return self._has_group(num_or_name)

    def make_group(self, name, descr, num=None) -> ExpGroup:
        self._update()
        return self._make_group(name, descr, num)

    def destroy_group(self, num_or_name):
        self._update()
        self._destroy_group(num_or_name)

    def group(self, num_or_name) -> ExpGroup:
        self._update()
        return self._group(num_or_name)

    def groups(self):
        self._update()
        return self._groups()

    def has_exp(self, dot_num: str) -> bool:
        self._update()
        return self._has_exp(dot_num)

    def make_exp(self, group_num_or_name, name, descr, num=None) -> Exp:
        self._update()
        return self._make_exp(group_num_or_name, name, descr, num)

    def destroy_exp(self, dot_num: str):
        self._update()
        self._destroy_exp(dot_num)

    def exp(self, dot_num: str) -> Exp:  # dot_num: '1.1', '1.10', '2.3'...
        self._update()
        return self._exp(dot_num)

    def exps(self, group_num_or_name=None):
        self._update()
        return self._exps(group_num_or_name)

    def start(self, exp_dot_num: str = None, autostart_next=False):
        self._update()
        self._start(exp_dot_num, autostart_next)

    def move_exp(self, dot_num, new_dot_num):
        self._update()
        self._move_exp(dot_num, new_dot_num)

    def _has_group(self, num_or_name): return self._has_child_num_or_name(num_or_name)

    def _make_group(self, name, descr, num=None) -> ExpGroup:
        return self._make_child(name, descr, num)

    def _destroy_group(self, num_or_name): self._destroy_child(num_or_name)

    def _group(self, num_or_name) -> ExpGroup: return self._get_child_by_num_or_name(num_or_name)

    def _groups(self): return self._children()

    def _has_exp(self, dot_num: str) -> bool:
        group_num, exp_num = util.parse_group_and_exp_num(dot_num)
        return self._group(group_num)._has_exp(exp_num)

    def _make_exp(self, group_num_or_name, name, descr, num=None) -> Exp:
        group = self._group(group_num_or_name)
        exp = group._make_exp(name, descr, num)
        return exp

    def _destroy_exp(self, dot_num: str):
        group_num, exp_num = util.parse_group_and_exp_num(dot_num)
        self._group(group_num)._destroy_exp(exp_num)

    def _exp(self, dot_num: str) -> Exp:  # dot_num: '1.1', '1.10', '2.3'...
        group_num, exp_num = util.parse_group_and_exp_num(dot_num)
        return self._group(group_num)._exp(exp_num)

    def _exps(self, group_num_or_name=None):
        if group_num_or_name is not None:
            return self._group(group_num_or_name)._exps()
        result = []
        for it in self._groups():
            result.extend(it.exps())
        return result

    def _start(self, exp_dot_num: str = None, autostart_next=False):
        if exp_dot_num is None:
            exp = None
            for group in self._groups():
                exp = group._get_exp_for_start()
                if exp is not None:
                    exp._start()
                    break
            if exp is None:
                raise NothingToDoXManError(f"There's nothing to start in the proj `{self}`!")
        else:
            self._exp(exp_dot_num)._start()
        if autostart_next:
            self._start(autostart_next=True)

    def _move_exp(self, dot_num, new_dot_num):
        pass  # TODO

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
        super().__init__(location_dir)

    def __str__(self): return f"Proj [{self._status}] {self._data.name} - {self._data.descr}"
