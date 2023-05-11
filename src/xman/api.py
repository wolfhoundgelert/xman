from typing import Any, Optional

from .error import NotImplementedXManError
from .proj import ExpProj
from .exp import Exp
from .group import ExpGroup
from .struct import ExpStructStatus, ExpStruct
from .structbox import ExpStructBox


def _get_exp_api(exp):
    if exp._api is None:
        ExpAPI(exp)
    return exp._api


def _get_exps_apis(exps): return [_get_exp_api(exp) for exp in exps]


def _get_group_api(group):
    if group._api is None:
        ExpGroupAPI(group)
    return group._api


def _get_groups_apis(groups): return [_get_group_api(group) for group in groups]


class StatusAPI:

    EMPTY = 'EMPTY'
    TODO = 'TODO'
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'
    ERROR = 'ERROR'
    SUCCESS = 'SUCCESS'
    FAIL = 'FAIL'

    @property
    def status(self) -> str: return self.__obj.status

    @property
    def resolution(self) -> str: return self.__obj.resolution

    @property
    def manual(self) -> str: return self.__obj.manual

    @property
    def workflow(self) -> str: return self.__obj.workflow

    @property
    def next(self) -> Optional[str]: return self.__obj.next

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle): p.text(str(self) if not cycle else '...')

    def __init__(self, obj: ExpStructStatus): self.__obj = obj

    def __str__(self): return str(self.__obj)


class ExpStructAPI:

    @property
    def location_dir(self) -> str: return self.__obj.location_dir

    @property
    def num(self) -> int: return self.__obj.num

    @property
    def name(self) -> str:
        self.__obj._update()
        return self.__obj._name

    @property
    def descr(self) -> str:
        self.__obj._update()
        return self.__obj._descr

    @property
    def status(self) -> StatusAPI:
        self.__obj._update()
        return StatusAPI(self.__obj._status)

    @property
    def manual(self) -> bool:
        self.__obj._update()
        return self.__obj._manual

    def tree(self):
        self.__obj._update()
        self.__obj._tree()

    def info(self):
        self.__obj._update()
        text = self.__obj._info()
        print(text)

    def start(self):
        self.__obj._update()
        self.__obj._start()

    def set_manual_status(self, status: str, resolution: str) -> 'ExpStructAPI':
        self.__obj._update()
        self.__obj._set_manual_status(status, resolution)
        return self

    def delete_manual_status(self, need_confirm=True) -> Optional['ExpStructAPI']:
        self.__obj._update()
        obj = self.__obj._delete_manual_status(need_confirm)
        return None if obj is None else self

    def edit(self, name=None, descr=None):
        self.__obj._update()
        self.__obj._edit(name, descr)

    def _update(self):
        self.__obj._update()

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle): p.text(str(self) if not cycle else '...')

    def __init__(self, obj: ExpStruct):
        self.__obj = obj
        obj._api = self

    def __str__(self): return str(self.__obj)


class ExpAPI(ExpStructAPI):

    @property
    def state(self) -> str:
        self.__obj._update()
        return self.__obj._state

    @property
    def idle(self) -> bool:
        self.__obj._update()
        return self.__obj._idle

    @property
    def result(self) -> Optional[Any]:
        self.__obj._update()
        return self.__obj._result

    @property
    def error(self) -> Optional[str]:
        self.__obj._update()
        return self.__obj._error

    @property
    def error_stack(self) -> Optional[str]:
        self.__obj._update()
        return self.__obj._error_stack

    def make_pipeline(self, run_func, params, save=False) -> 'ExpAPI':
        self.__obj._update()
        self.__obj._make_pipeline(run_func, params, save)
        return self

    def destroy_pipeline(self, need_confirm=True) -> Optional['ExpAPI']:
        self.__obj._update()
        obj = self.__obj._destroy_pipeline(need_confirm)
        return None if obj is None else self

    def start(self):
        self.__obj._update()
        self.__obj._start()
        return self

    def set_manual_result(self, result, need_confirm=True) -> Optional['ExpAPI']:
        self.__obj._update()
        obj = self.__obj._set_manual_result(result, need_confirm)
        return None if obj is None else self

    def delete_manual_result(self, need_confirm=True) -> Optional['ExpAPI']:
        self.__obj._update()
        obj = self.__obj._delete_manual_result(need_confirm)
        return None if obj is None else self

    def success(self, resolution: str) -> Optional['ExpAPI']:
        self.__obj._update()
        self.__obj._success(resolution)
        return self

    def fail(self, resolution: str) -> Optional['ExpAPI']:
        self.__obj._update()
        self.__obj._fail(resolution)
        return self

    def __init__(self, obj: Exp):
        super().__init__(obj)
        self.__obj = obj


class ExpStructBoxAPI(ExpStructAPI):

    @property
    def num_children(self) -> int:
        self.__obj._update()
        return self.__obj._num_children

    def __init__(self, obj: ExpStructBox):
        super().__init__(obj)
        self.__obj = obj


class ExpGroupAPI(ExpStructBoxAPI):

    def has_exp(self, num_or_name) -> bool:
        self.__obj._update()
        return self.__obj._has_exp(num_or_name)

    def make_exp(self, name, descr, num=None) -> ExpAPI:
        self.__obj._update()
        exp = self.__obj._make_exp(name, descr, num)
        return _get_exp_api(exp)

    def destroy_exp(self, num_or_name, need_confirm=True):
        self.__obj._update()
        self.__obj._destroy_exp(num_or_name, need_confirm)

    def exp(self, num_or_name) -> ExpAPI:
        self.__obj._update()
        exp = self.__obj._exp(num_or_name)
        return _get_exp_api(exp)

    def exps(self) -> [ExpAPI]:
        self.__obj._update()
        exps = self.__obj._exps()
        return _get_exps_apis(exps)

    def get_exp_for_start(self) -> Optional[ExpAPI]:
        self.__obj._update()
        exp = self.__obj._get_exp_for_start()
        return None if exp is None else _get_exp_api(exp)

    def start(self, exp_num=None, autostart_next=False):
        self.__obj._update()
        self.__obj._start(exp_num, autostart_next)

    def change_exp_num(self, num_or_name):  # TODO
        self.__obj._update()
        self.__obj._change_exp_num(num_or_name)

    def __init__(self, obj: ExpGroup):
        super().__init__(obj)
        self.__obj = obj


class ExpProjAPI(ExpStructBoxAPI):

    @property
    def num(self) -> int:
        raise NotImplementedXManError(f"`num` property isn't supported for a project!")

    def has_group(self, num_or_name) -> bool:
        self.__obj._update()
        return self.__obj._has_group(num_or_name)

    def make_group(self, name, descr, num=None) -> ExpGroupAPI:
        self.__obj._update()
        group = self.__obj._make_group(name, descr, num)
        return _get_group_api(group)

    def destroy_group(self, num_or_name, need_confirm=True):
        self.__obj._update()
        self.__obj._destroy_group(num_or_name, need_confirm)

    def group(self, num_or_name) -> ExpGroupAPI:
        self.__obj._update()
        group = self.__obj._group(num_or_name)
        return _get_group_api(group)

    def groups(self) -> [ExpGroupAPI]:
        self.__obj._update()
        groups = self.__obj._groups()
        return _get_groups_apis(groups)

    def has_exp(self, dot_num: str) -> bool:
        self.__obj._update()
        return self.__obj._has_exp(dot_num)

    def make_exp(self, group_num_or_name, name, descr, num=None) -> ExpAPI:
        self.__obj._update()
        exp = self.__obj._make_exp(group_num_or_name, name, descr, num)
        return _get_exp_api(exp)

    def destroy_exp(self, dot_num: str, need_confirm=True):
        self.__obj._update()
        self.__obj._destroy_exp(dot_num, need_confirm)

    def exp(self, dot_num: str) -> ExpAPI:  # dot_num: '1.1', '1.10', '2.3'...
        self.__obj._update()
        exp = self.__obj._exp(dot_num)
        return _get_exp_api(exp)

    def exps(self, group_num_or_name=None) -> [ExpAPI]:
        self.__obj._update()
        exps = self.__obj._exps(group_num_or_name)
        return _get_exps_apis(exps)

    def start(self, exp_dot_num: str = None, autostart_next=False):
        self.__obj._update()
        self.__obj._start(exp_dot_num, autostart_next)

    def move_exp(self, dot_num, new_dot_num):  # TODO
        self.__obj._update()
        self.__obj._move_exp(dot_num, new_dot_num)

    def __init__(self, obj: ExpProj):
        super().__init__(obj)
        self.__obj = obj
