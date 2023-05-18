from typing import Optional, List

from .error import NothingToDoXManError
from .struct import ExpStructStatus
from .structbox import ExpStructBox
from .exp import Exp, ExpState


class ExpGroup(ExpStructBox):

    def has_exp(self, num_or_name): return self.has_child_with_num_or_name(num_or_name)

    def make_exp(self, name, descr, num=None) -> Exp: return self.make_child(name, descr, num)

    def change_exp_num(self, num_or_name, new_num):
        exp = self.exp(num_or_name)
        exp._check_not_active()
        self._change_child_num(num_or_name, new_num)

    def delete_exp(self, num_or_name, need_confirm=True):
        exp = self.exp(num_or_name)
        exp._check_not_active()
        self.delete_child(num_or_name, need_confirm)

    def exp(self, num_or_name) -> Exp: return self.get_child_by_num_or_name(num_or_name)

    def exps(self) -> List[Exp]: return self.children

    def filter_exps(self, active=None, manual=None, ready_for_start=None) -> List[Exp]:
        result = self.exps()
        if active is not None:
            result = [x for x in result if x.is_active == active]
        if manual is not None:
            result = [x for x in result if x.is_manual == manual]
        if ready_for_start is not None:
            result = [x for x in result if x.is_ready_for_start == ready_for_start]
        return result

    def get_exp_for_start(self) -> Optional[Exp]:
        for child in self.children:
            if child.status == ExpStructStatus.IN_PROGRESS and child.state == ExpState.IDLE:
                return child
        return self.get_child_by_auto_status(ExpStructStatus.TODO)

    def start(self, exp_num_or_name=None, autostart_next=False):
        if exp_num_or_name is None:
            exp = self.get_exp_for_start()
            if exp is None:
                raise NothingToDoXManError(f"There's nothing to start in the group `{self}`!")
            exp.start()
        else:
            self.exp(exp_num_or_name).start()
        if autostart_next:
            self.start(autostart_next=True)

    def update(self):
        if self.__updating:
            return
        self.__updating = True
        super().update()
        # Status should be updated at the end of the inherited updating hierarchy
        if type(self) == ExpGroup:
            self._update_status()
        self.__updating = False

    def __init__(self, location_dir, parent):
        self.__updating = False
        super().__init__(location_dir, parent)
        from .api import ExpGroupAPI
        self._api = ExpGroupAPI(self)

    def __str__(self):
        return f"Group {self.num} [{self.status}] {self._data.name} - {self._data.descr}"
