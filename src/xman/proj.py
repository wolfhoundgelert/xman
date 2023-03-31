from .struct import ExpStructData, ExpStruct, ExpStructStatus
from .group import ExpGroup
from .exp import Exp
from . import util

import os
import shutil


class ExpProjData(ExpStructData):

    def __init__(self, name, descr):
        super().__init__(name, descr)


class ExpProjStatus(ExpStructStatus):

    def __init__(self, status: str):
        super().__init__(status)

    def _workflow(self):
        return (ExpStructStatus.TODO,
                ExpStructStatus.IN_PROGRESS,
                ExpStructStatus.DONE,
                (ExpStructStatus.SUCCESS, ExpStructStatus.FAIL))


class ExpProj(ExpStruct):

    _PROJ_FILE = 'exp_proj.pkl'

    @staticmethod
    def _get_proj_file(location_dir):
        return os.path.join(location_dir, ExpProj._PROJ_FILE)

    @staticmethod
    def _make(location_dir, name, descr):
        location_dir = util._make_dir(location_dir)
        data = ExpProjData(name, descr)
        proj = ExpProj(location_dir, data)
        proj._save_data()
        return proj

    @staticmethod
    def _load(location_dir):
        data = ExpStruct._load_data(location_dir, ExpProj._PROJ_FILE)
        return ExpProj(location_dir, data)

    def __init__(self, location_dir, data):
        super().__init__(location_dir, data)
        self.__num_to_group = None
        self.__name_to_group = None
        self._update()

    def __str__(self):
        s = f"Proj [{self.status()}] {self.data.name} - {self.data.descr}"
        for it in self.groups():
            s += '\n\n    ' + str(it).replace('\n', '\n    ')
        return s

    def _file_path(self):
        return ExpProj._get_proj_file(self.location_dir)

    # TODO add last changes timestamp for the whole project or exact section and compare the version
    #  (don't need to update if they are equals)
    def _update(self):
        if not super()._update():
            return
        self.__num_to_group = {}
        self.__name_to_group = {}
        nums = util._get_dir_nums_by_pattern(self.location_dir, ExpGroup._GROUP_DIR_PREFIX)
        for num in nums:
            group = ExpGroup._load(self.location_dir, num)
            self.__num_to_group[num] = group
            self.__name_to_group[group.data.name] = group
        self.status = ExpProjStatus(ExpStructStatus.TODO)  # TODO calculate status depends on exps

    def has_group(self, num_or_name):
        self._update()
        return util._has_in_num_or_name_dicts(num_or_name, self.__num_to_group, self.__name_to_group)

    def make_group(self, name, descr, num=None) -> ExpGroup:
        self._update()
        util._check_num(num, True)
        if name in self.__name_to_group:
            raise ValueError(f"A group with the name `{name}` already exists!")
        if num is not None:
            if num in self.__num_to_group:
                raise ValueError(f"A group with the num `{num}` already exists!")
        else:
            num = util._get_highest_num_in_dict(self.__num_to_group) + 1
        group = ExpGroup._make(self.location_dir, num, name, descr)
        self.__num_to_group[num] = group
        self.__name_to_group[name] = group
        return group

    def remove_group(self, num_or_name):
        self._update()
        group = self.group(num_or_name)
        num = group.num
        name = group.data.name
        group_dir = ExpGroup._get_group_dir(self.location_dir, num)
        response = input(f"ACHTUNG! Remove `{group_dir}` dir with all its content? (y/n) ")
        if response.lower() != "y":
            return
        del self.__num_to_group[num]
        del self.__name_to_group[name]
        shutil.rmtree(group_dir)

    def group(self, num_or_name) -> ExpGroup:
        self._update()
        return util._get_by_num_or_name(num_or_name, self.__num_to_group, self.__name_to_group)

    def groups(self):
        self._update()
        return list(self.__num_to_group.values())

    def has_exp(self, dot_num: float) -> bool:
        self._update()
        group_num, exp_num = util._parse_group_and_exp_num(dot_num)
        return self.group(group_num).has_exp(exp_num)

    def make_exp(self, group_num_or_name, name, descr, num=None) -> Exp:
        self._update()
        return self.group(group_num_or_name).make_exp(name, descr, num)

    def remove_exp(self, dot_num: float):
        self._update()
        group_num, exp_num = util._parse_group_and_exp_num(dot_num)
        self.group(group_num).remove_exp(exp_num)

    def exp(self, dot_num: float) -> Exp:  # 1.1, 1.2, 2.3...
        self._update()
        group_num, exp_num = util._parse_group_and_exp_num(dot_num)
        return self.group(group_num).exp(exp_num)

    def exps(self, group_num_or_name=None):
        self._update()
        if group_num_or_name is not None:
            return self.group(group_num_or_name).exps()
        result = []
        for it in self.groups():
            result.extend(it.exp())
        return result
