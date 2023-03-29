from .struct import ExpStructData, ExpStruct, ExpStructStatus
from .exp import Exp
from . import util

import os
import shutil


class ExpGroupData(ExpStructData):

    def __init__(self, name, descr):
        super().__init__(name, descr)


class ExpGroupStatus(ExpStructStatus):

    def __init__(self, status: str):
        super().__init__(status)

    def _workflow(self):
        return (ExpStructStatus.TODO,
                ExpStructStatus.IN_PROGRESS,
                ExpStructStatus.DONE,
                (ExpStructStatus.SUCCESS, ExpStructStatus.FAIL))


class ExpGroup(ExpStruct):

    _GROUP_DIR_PREFIX = 'group'
    _GROUP_FILE = 'exp_group.pkl'

    @staticmethod
    def _get_group_dir(proj_location_dir, num):
        return os.path.join(proj_location_dir, ExpGroup._GROUP_DIR_PREFIX + str(num))

    @staticmethod
    def _get_group_file(location_dir):
        return os.path.join(location_dir, ExpGroup._GROUP_FILE)

    @staticmethod
    def _make(proj_location_dir, num, name, descr):
        location_dir = ExpGroup._get_group_dir(proj_location_dir, num)
        location_dir = util._make_dir(location_dir)
        data = ExpGroupData(name, descr)
        group = ExpGroup(location_dir, num, data)
        group._save_data()
        return group

    @staticmethod
    def _load(proj_location_dir, num):
        location_dir = ExpGroup._get_group_dir(proj_location_dir, num)
        data = ExpStruct._load_data(location_dir, ExpGroup._GROUP_FILE)
        return ExpGroup(location_dir, num, data)

    def __init__(self, location_dir: str, num: int, data: ExpGroupData):
        super().__init__(location_dir, data)
        util._check_num(num, False)
        self.location_dir = location_dir
        self.num = num
        self.data = data
        self.__num_to_exp = None
        self.__name_to_exp = None
        self.status = None
        self._update()

    def __str__(self):
        el = self.str_exps()
        return f"Group {self.num}, name `{self.data.name}`, descr `{self.data.descr}`, status `{self.status}`, exps {el}"

    def _file_path(self):
        return ExpGroup._get_group_file(self.location_dir)

    def _update(self):
        if not super()._update():
            return
        self.__num_to_exp = {}
        self.__name_to_exp = {}
        nums = util._get_dir_nums_by_pattern(self.location_dir, Exp._EXP_DIR_PREFIX)
        for num in nums:
            exp = Exp._load(self.location_dir, num)
            self.__num_to_exp[num] = exp
            self.__name_to_exp[exp.data.name] = exp
        self.status = None  # TODO

    def has_exp(self, num_or_name):
        self._update()
        return util._has_in_num_or_name_dicts(num_or_name, self.__num_to_exp, self.__name_to_exp)

    def make_exp(self, name, descr, num=None) -> Exp:
        self._update()
        util._check_num(num, True)
        if name in self.__name_to_exp:
            raise ValueError(f"An experiment with the name `{name}` already exists!")
        if num is not None:
            if num in self.__num_to_exp:
                raise ValueError(f"An experiment with the num `{num}` already exists!")
        else:
            num = util._get_highest_num_in_dict(self.__num_to_exp) + 1
        exp = Exp._make(self.location_dir, num, name, descr)
        self.__num_to_exp[num] = exp
        self.__name_to_exp[name] = exp
        return exp

    def remove_exp(self, num_or_name):
        self._update()
        exp = self.exp(num_or_name)
        num = exp.num
        name = exp.data.name
        exp_dir = Exp._get_exp_dir(self.location_dir, num)
        response = input(f"ACHTUNG! Remove `{exp_dir}` dir with all its content? (y/n) ")
        if response.lower() != "y":
            return
        del self.__num_to_exp[num]
        del self.__name_to_exp[name]
        shutil.rmtree(exp_dir)

    def exp(self, num_or_name) -> Exp:
        self._update()
        return util._get_by_num_or_name(num_or_name, self.__num_to_exp, self.__name_to_exp)

    def exps(self):
        self._update()
        return list(self.__num_to_exp.values())

    def str_exps(self):
        self._update()
        return [str(it) for it in self.exps()]
