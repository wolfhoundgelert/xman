from .error import NothingToDoXManError
from .structbox import ExpStructBox
from .group import ExpGroup
from .exp import Exp
from . import util


class ExpProj(ExpStructBox):

    def __init__(self, location_dir):
        self.__updating = False
        super().__init__(location_dir)

    def __str__(self): return f"Proj [{self._status}] {self._data.name} - {self._data.descr}"

    def _update(self):
        if self.__updating:
            return
        self.__updating = True
        super()._update()
        # Status should be updated at the end of the inherited updating hierarchy
        if type(self) == ExpProj:
            self._update_status()
        self.__updating = False

    def has_group(self, num_or_name): return self._has_child_num_or_name(num_or_name)

    def make_group(self, name, descr, num=None) -> ExpGroup: return self._make_child(name, descr, num)

    def destroy_group(self, num_or_name): return self._destroy_child(num_or_name)

    def group(self, num_or_name) -> ExpGroup: return self._get_child_by_num_or_name(num_or_name)

    def groups(self): return self._children()

    def has_exp(self, dot_num: str) -> bool:
        group_num, exp_num = util.parse_group_and_exp_num(dot_num)
        return self.group(group_num).has_exp(exp_num)

    def make_exp(self, group_num_or_name, name, descr, num=None) -> Exp:
        group = self.group(group_num_or_name)
        exp = group.make_exp(name, descr, num)
        return exp

    def destroy_exp(self, dot_num: str):
        group_num, exp_num = util.parse_group_and_exp_num(dot_num)
        return self.group(group_num).destroy_exp(exp_num)

    def exp(self, dot_num: str) -> Exp:  # dot_num: '1.1', '1.10', '2.3'...
        group_num, exp_num = util.parse_group_and_exp_num(dot_num)
        return self.group(group_num).exp(exp_num)

    def exps(self, group_num_or_name=None):
        if group_num_or_name is not None:
            return self.group(group_num_or_name).exps()
        result = []
        for it in self.groups():
            result.extend(it.exps())
        return result

    def start(self, exp_dot_num: str = None, autostart_next=False):
        if exp_dot_num is None:
            exp = None
            for group in self.groups():
                exp = group.get_exp_for_start()
                if exp is not None:
                    exp.start()
                    break
            if exp is None:
                raise NothingToDoXManError(f"There's nothing to start in the proj `{self}`!")
        else:
            self.exp(exp_dot_num).start()
        if autostart_next:
            self.start(autostart_next=True)

    def move_exp(self, dot_num, new_dot_num):
        pass  # TODO
