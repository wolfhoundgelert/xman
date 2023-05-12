from typing import Optional

from .error import NothingToDoXManError
from .struct import ExpStructStatus
from .structbox import ExpStructBox
from .exp import Exp, ExpState


class ExpGroup(ExpStructBox):

    def _has_exp(self, num_or_name): return self._has_child_num_or_name(num_or_name)

    def _make_exp(self, name, descr, num=None) -> Exp: return self._make_child(name, descr, num)

    def _destroy_exp(self, num_or_name, need_confirm=True):
        self._destroy_child(num_or_name, need_confirm)

    def _exp(self, num_or_name) -> Exp: return self._get_child_by_num_or_name(num_or_name)

    def _exps(self): return self._children()

    def _get_exp_for_start(self) -> Optional[Exp]:
        for child in self._children():
            if child._status == ExpStructStatus.IN_PROGRESS and child._state == ExpState.IDLE:
                return child
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

    def __init__(self, location_dir, parent):
        self.__updating = False
        super().__init__(location_dir, parent)

    def __str__(self):
        return f"Group {self.num} [{self._status}] {self._data.name} - {self._data.descr}"
