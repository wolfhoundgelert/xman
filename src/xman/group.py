from typing import Optional, List, Callable

from . import filter
from .error import NothingToDoXManError, IllegalOperationXManError
from .structbox import ExpStructBox
from .exp import Exp


class ExpGroup(ExpStructBox):

    def update(self):
        if self.__updating:
            return
        self.__updating = True
        super().update()
        # Status should be updated at the end of the inherited updating hierarchy
        if type(self) == ExpGroup:
            self._update_status()
        self.__updating = False

    def has_exp(self, num_or_name) -> bool: return self.has_child(num_or_name)

    def exp(self, num_or_name) -> Exp: return self.child(num_or_name)

    def make_exp(self, name, descr, num=None) -> Exp: return self.make_child(name, descr, num)

    def delete_exp(self, num_or_name, need_confirm=True) -> bool:
        self.exp(num_or_name)._check_is_not_active()
        return self.delete_child(num_or_name, need_confirm)

    def exps(self) -> List[Exp]: return self.children()

    def num_exps(self) -> int: return self.num_children()

    def exps_nums(self) -> List[int]: return self.children_nums()

    def exps_names(self) -> List[str]: return self.children_names()

    def change_exp_num(self, num_or_name, new_num):
        self.exp(num_or_name)._check_is_not_active()
        self.change_child_num(num_or_name, new_num)

    def filter_exps(self,
                    mode: str = 'AND',
                    custom_filter: Callable[[Exp], bool] = None,
                    is_active: bool = None,
                    is_manual: bool = None,
                    is_ready_for_start: bool = None,
                    status_or_list: str | List[str] = None,
                    not_status_or_list: str | List[str] = None,
                    ) -> List[Exp]:
        return filter.exps(self.exps(), mode, custom_filter, is_active, is_manual,
                           is_ready_for_start, status_or_list, not_status_or_list)

    def get_exp_for_start(self) -> Optional[Exp]:
        ready_list = self.filter_exps(is_ready_for_start=True)
        return ready_list[0] if len(ready_list) else None

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

    def _check_has_no_active_exps(self):
        active_list = self.filter_exps(is_active=True)
        if len(active_list):
            raise IllegalOperationXManError(
                f"Illegal operation while there's any active experiment in the `{self}` - found:"
                f"{active_list}!")

    def __init__(self, location_dir, parent):
        from .api import ExpGroupAPI
        self.__updating = False
        super().__init__(location_dir, parent)
        self._api = ExpGroupAPI(self)

    def __str__(self):
        return f"Group {self.num} [{self.status}] {self._data.name} - {self._data.descr}"
