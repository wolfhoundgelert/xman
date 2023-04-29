from .error import NothingToDoXManError
from .struct import ExpStructStatus, ExpStructBox
from .exp import Exp
from . import platform


class ExpGroup(ExpStructBox):

    @staticmethod
    def _dir_prefix(): return 'group'

    def __init__(self, location_dir, name, descr):
        self.__updating = False
        super().__init__(location_dir, name, descr)

    def __str__(self): return f"Group {self.num} [{self._status}] {self._data.name} - {self._data.descr}"

    def _get_child_class(self): return Exp

    def _update(self):
        if self.__updating:
            return
        self.__updating = True
        super()._update()
        # Status should be updated at the end of the inherited updating hierarchy
        if type(self) == ExpGroup:
            self._update_status()
        self.__updating = False

    def has_exp(self, num_or_name): return self._has_child_num_or_name(num_or_name)

    def make_exp(self, name, descr, num=None) -> Exp:
        exp = self._make_child(name, descr, num)
        return exp if platform.check_forked_folders(self) else None

    def destroy_exp(self, num_or_name):
        exp = self._destroy_child(num_or_name)
        return exp

    def exp(self, num_or_name) -> Exp: return self._get_child_by_num_or_name(num_or_name)

    def exps(self): return self._children()

    def get_exp_for_start(self):
        # TODO Support IN_PROGRESS with state IDLE
        return self._get_child_by_status(ExpStructStatus.TODO)

    def start(self, exp_num=None, autostart_next=False):
        if exp_num is None:
            exp = self.get_exp_for_start()
            if exp is None:
                raise NothingToDoXManError(f"There's nothing to start in the group `{self}`!")
            exp.start()
        else:
            self.exp(exp_num).start()
        if autostart_next:
            self.start(autostart_next=True)

    def change_exp_num(self, num_or_name):
        pass  # TODO
