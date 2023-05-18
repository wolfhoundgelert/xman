from typing import Optional, List

from .api import ExpGroupAPI
from .error import NothingToDoXManError, ArgumentsXManError
from .struct import ExpStructStatus
from .structbox import ExpStructBox
from .exp import Exp, ExpState


class ExpGroup(ExpStructBox):

    def _has_exp(self, num_or_name): return self._has_child_num_or_name(num_or_name)

    def _make_exp(self, name, descr, num=None) -> Exp: return self._make_child(name, descr, num)

    def _change_exp_num(self, num_or_name, new_num):
        exp = self._exp(num_or_name)
        exp._check_not_active()
        self._change_child_num(num_or_name, new_num)

    def _destroy_exp(self, num_or_name, need_confirm=True):
        exp = self._exp(num_or_name)
        exp._check_not_active()
        self._destroy_child(num_or_name, need_confirm)

    def _exp(self, num_or_name) -> Exp: return self._get_child_by_num_or_name(num_or_name)

    def _exps(self) -> [Exp]: return self._children()

    def _filter_exps(self, active=None, manual=None) -> [Exp]:
        if active is None and manual is None:
            raise ArgumentsXManError(f"There's nothing to filter - specify `active` or `manual` "
                                     f"params!")
        if active == manual == True:
            raise ArgumentsXManError(f"Manual experiments can't be active!")
        if active is not None and manual is not None:
            return [x for x in self._exps() if x._is_active == active and x._is_manual == manual]
        if active is None:
            return [x for x in self._exps() if x._is_manual == manual]
        if manual is None:
            return [x for x in self._exps() if x._is_active == active]

    def _get_exp_for_start(self) -> Optional[Exp]:
        for child in self._children():
            if child._status == ExpStructStatus.IN_PROGRESS and child._state == ExpState.IDLE:
                return child
        return self._get_child_by_auto_status(ExpStructStatus.TODO)

    def _start(self, exp_num_or_name=None, autostart_next=False):
        if exp_num_or_name is None:
            exp = self._get_exp_for_start()
            if exp is None:
                raise NothingToDoXManError(f"There's nothing to start in the group `{self}`!")
            exp._start()
        else:
            self._exp(exp_num_or_name)._start()
        if autostart_next:
            self._start(autostart_next=True)

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
        self._api = ExpGroupAPI(self)

    def __str__(self):
        return f"Group {self._num} [{self._status}] {self._data.name} - {self._data.descr}"
