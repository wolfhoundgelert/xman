from .struct import ExpStructData, ExpStruct, ExpStructStatus
from .exp import Exp
from . import util

import os
import shutil


class ExpGroup(ExpStruct):

    _GROUP_DIR_PREFIX = 'group'

    @staticmethod
    def _get_group_dir(proj_location_dir, num):
        return os.path.join(proj_location_dir, ExpGroup._GROUP_DIR_PREFIX + str(num))

    @staticmethod
    def _make(proj_location_dir, num, name, descr):
        util._check_num(num, False)
        location_dir = ExpGroup._get_group_dir(proj_location_dir, num)
        return ExpStruct._make(ExpStructData, ExpGroup, location_dir, name, descr)

    @staticmethod
    def _load(proj_location_dir, num):
        util._check_num(num, False)
        location_dir = ExpGroup._get_group_dir(proj_location_dir, num)
        return ExpStruct._load(ExpGroup, location_dir)

    def __str__(self):
        s = f"Group {self.num} [{self.status}] {self.data.name} - {self.data.descr}"
        for it in self.exps():
            s += '\n    ' + str(it)
        return s

    def _update(self):
        if not super()._update():
            return False
        self.__num_to_exp = {}
        self.__name_to_exp = {}
        nums = util._get_dir_nums_by_pattern(self.location_dir, Exp._EXP_DIR_PREFIX)
        for num in nums:
            exp = Exp._load(self.location_dir, num)
            self.__num_to_exp[num] = exp
            self.__name_to_exp[exp.data.name] = exp
        self.status = ExpStructStatus(ExpStructStatus.EMPTY)  # TODO calculate status depends on exps
        return True

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

    def start(self):
        self._update()
        pass  # TODO
        # TODO group.start() - seeking the best candidate for running (IN_PROGRESS_NOT_ACTIVE),
        #  group.start(exp_num) - run given exact experiment, e.g. 1
