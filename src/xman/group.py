from .struct import ExpStruct, ExpStructBox
from .exp import Exp


class ExpGroup(ExpStructBox):

    @staticmethod
    def _dir_prefix():
        return 'group'

    def __str__(self):
        s = f"Group {self.num} [{self.status}] {self.data.name} - {self.data.descr}"
        for it in self.exps():
            s += '\n    ' + str(it)
        return s

    def _get_child_class(self):
        return Exp

    def has_exp(self, num_or_name):
        return self._has_child_num_or_name(num_or_name)

    def make_exp(self, name, descr, num=None) -> Exp:
        return self._make_child(name, descr, num)

    def remove_exp(self, num_or_name):
        self._remove_child(num_or_name)

    def exp(self, num_or_name) -> Exp:
        return self._get_child_by_num_or_name(num_or_name)

    def exps(self):
        return self._children()

    def start(self):
        pass  # TODO
        # TODO group.start() - seeking the best candidate for running (IN_PROGRESS_NOT_ACTIVE),
        #  group.start(exp_num) - run given exact experiment, e.g. 1
