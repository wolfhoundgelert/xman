from typing import Optional, List, Callable

from . import filter, exp_helper
from .error import NothingToDoXManError, IllegalOperationXManError
from .structbox import ExpStructBox
from .exp import Exp


class ExpGroup(ExpStructBox):

    @property
    def proj(self) -> 'ExpProj': return self.parent

    def info(self) -> str: return exp_helper.get_info_with_marked_exps(self)

    def update(self):
        if self.__updating:
            return
        self.__updating = True
        super().update()
        # Status should be updated at the end of the inherited updating hierarchy
        if type(self) == ExpGroup:
            self._update_status()
        self.__updating = False

    def has_exp(self, num_or_name: int | str) -> bool: return self.has_child(num_or_name)

    def exp(self, num_or_name: int | str) -> Exp: return self.child(num_or_name)

    def make_exp(self, name: str, descr: str, num: int = None) -> Exp:
        return self.make_child(name, descr, num)

    def delete_exp(self, num_or_name: int | str, need_confirm: bool = True) -> bool:
        self.exp(num_or_name)._check_is_not_active()
        return self.delete_child(num_or_name, need_confirm)

    def exps(self) -> List[Exp]: return self.children()

    def num_exps(self) -> int: return self.num_children()

    def exps_nums(self) -> List[int]: return self.children_nums()

    def exps_names(self) -> List[str]: return self.children_names()

    def change_exp_num(self, num_or_name: int | str, new_num: int):
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
                    has_marker: bool = None,
                    marker_or_list: str | List[str] = None,
                    ) -> List[Exp]:
        return filter.exps(self.exps(), mode, custom_filter, is_active, is_manual,
                is_ready_for_start, status_or_list, not_status_or_list, has_marker, marker_or_list)

    def get_exp_for_start(self) -> Optional[Exp]:
        ready_list = self.filter_exps(is_ready_for_start=True)
        return ready_list[0] if len(ready_list) else None

    def start(self, exp_num_or_name: int | str = None, autostart_next: bool = False):
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
        return f"Group {self.num} [{self.status}] {self.name} - {self.descr}"
