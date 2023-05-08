from .error import NothingToDoXManError
from .struct import ExpStructStatus
from .structbox import ExpStructBox
from .exp import Exp


class ExpGroup(ExpStructBox):

    def has_exp(self, num_or_name):
        self._update()
        return self._has_exp(num_or_name)

    def make_exp(self, name, descr, num=None) -> Exp:
        self._update()
        return self._make_exp(name, descr, num)

    def destroy_exp(self, num_or_name):
        self._update()
        self._destroy_exp(num_or_name)

    def exp(self, num_or_name) -> Exp:
        self._update()
        return self._exp(num_or_name)

    def exps(self):
        self._update()
        return self._exps()

    def get_exp_for_start(self):
        self._update()
        return self._get_exp_for_start()

    def start(self, exp_num=None, autostart_next=False):
        self._update()
        self._start(exp_num, autostart_next)

    def change_exp_num(self, num_or_name):
        self._update()
        self._change_exp_num(num_or_name)

    def _has_exp(self, num_or_name): return self._has_child_num_or_name(num_or_name)

    def _make_exp(self, name, descr, num=None) -> Exp: return self._make_child(name, descr, num)

    def _destroy_exp(self, num_or_name): self._destroy_child(num_or_name)

    def _exp(self, num_or_name) -> Exp: return self._get_child_by_num_or_name(num_or_name)

    def _exps(self): return self._children()

    def _get_exp_for_start(self):
        # TODO Support IN_PROGRESS with state IDLE
        return self._get_child_by_status(ExpStructStatus.TODO)

    def _start(self, exp_num=None, autostart_next=False):
        if exp_num is None:
            exp = self._get_exp_for_start()
            if exp is None:
                raise NothingToDoXManError(f"There's nothing to start in the group `{self}`!")
            exp._start()
        else:
            self._exp(exp_num)._start()
        if autostart_next:
            self._start(autostart_next=True)

    def _change_exp_num(self, num_or_name):
        pass  # TODO

    def _update(self):
        if self.__updating:
            return
        self.__updating = True
        super()._update()
        # Status should be updated at the end of the inherited updating hierarchy
        if type(self) == ExpGroup:
            self._update_status()
        self.__updating = False

    def __init__(self, location_dir):
        self.__updating = False
        super().__init__(location_dir)

    def __str__(self):
        return f"Group {self.num} [{self._status}] {self._data.name} - {self._data.descr}"
