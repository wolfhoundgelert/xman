from .event import UpdateEvent
from .struct import ExpStructStatus, ExpStructBox
from .exp import Exp


class ExpGroup(ExpStructBox):

    @staticmethod
    def _dir_prefix():
        return 'group'

    def __str__(self):
        s = f"Group {self.num} [{self._status}] {self._data.name} - {self._data.descr}"
        for it in self.exps():
            s += '\n    ' + str(it)
        return s

    def _get_child_class(self):
        return Exp

    def _update_listener(self, event: UpdateEvent):
        event.group = self
        self._dispatch(event)

    def has_exp(self, num_or_name):
        return self._has_child_num_or_name(num_or_name)

    def make_exp(self, name, descr, num=None) -> Exp:
        exp = self._make_child(name, descr, num)
        self._dispatch(UpdateEvent(exp, self))
        return exp

    def remove_exp(self, num_or_name):
        exp = self._remove_child(num_or_name)
        self._dispatch(UpdateEvent(exp, self))

    def exp(self, num_or_name) -> Exp:
        return self._get_child_by_num_or_name(num_or_name)

    def exps(self):
        return self._children()

    def get_exp_for_start(self):
        # TODO Support IN_PROGRESS with type IDLE
        return self._get_child_by_status(ExpStructStatus.TODO)

    def start(self, exp_num=None, autostart_next=False):
        if exp_num is None:
            exp = self.get_exp_for_start()
            if exp is None:
                raise AssertionError(f"There's nothing to start in the group `{self}`!")
            exp.start()
        else:
            self.exp(exp_num).start()
        if autostart_next:
            self.start(autostart_next=True)
