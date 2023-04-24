from .struct import ExpStruct, ExpStructBox
from .group import ExpGroup
from .exp import Exp
from . import util


class ExpProj(ExpStructBox):

    @staticmethod
    def _dir_prefix():
        raise ValueError(f"Isn't supported by logic!")

    def __str__(self):
        s = f"Proj [{self.status}] {self._data.name} - {self._data.descr}"
        for it in self.groups():
            s += '\n\n    ' + str(it).replace('\n', '\n    ')
        return s

    def _get_child_class(self):
        return ExpGroup

    def has_group(self, num_or_name):
        return self._has_child_num_or_name(num_or_name)

    def make_group(self, name, descr, num=None) -> ExpGroup:
        return self._make_child(name, descr, num)

    def remove_group(self, num_or_name):
        self._remove_child(num_or_name)

    def group(self, num_or_name) -> ExpGroup:
        return self._get_child_by_num_or_name(num_or_name)

    def groups(self):
        return self._children()

    def has_exp(self, dot_num: str) -> bool:
        group_num, exp_num = util.parse_group_and_exp_num(dot_num)
        return self.group(group_num).has_exp(exp_num)

    def make_exp(self, group_num_or_name, name, descr, num=None) -> Exp:
        return self.group(group_num_or_name).make_exp(name, descr, num)

    def remove_exp(self, dot_num: str):
        group_num, exp_num = util.parse_group_and_exp_num(dot_num)
        self.group(group_num).remove_exp(exp_num)

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
            for group in self.groups():
                exp = group.get_exp_for_start()
                if exp is not None:
                    exp.start()
                    break;
            if exp is None:
                raise AssertionError(f"There's nothing to start in the proj `{self}`!")
        else:
            self.exp(exp_dot_num).start()
        if autostart_next:
            self.start(autostart_next=True)
