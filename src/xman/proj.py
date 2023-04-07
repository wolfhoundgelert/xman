from .struct import ExpStructData, ExpStruct, ExpStructStatus
from .group import ExpGroup
from .exp import Exp
from . import util
from . import helper

import shutil


class ExpProj(ExpStruct):

    @staticmethod
    def _make(location_dir, name, descr):
        return ExpStruct._make(ExpStructData, ExpProj, location_dir, name, descr)

    @staticmethod
    def _load(location_dir):
        return ExpStruct._load(ExpProj, location_dir)

    def __str__(self):
        s = f"Proj [{self.status}] {self.data.name} - {self.data.descr}"
        for it in self.groups():
            s += '\n\n    ' + str(it).replace('\n', '\n    ')
        return s

    def _file_path(self):
        return ExpProj._get_proj_file(self.location_dir)

    def _update(self):
        if not super()._update():
            return False
        # TODO the code below (also in group.py) should be a part of the base class ExpStructContainer,
        #  which should has self._num_to_child and etc. logic of container-children relations.
        self._num_to_child = {}
        self._name_to_child = {}
        nums = util._get_dir_nums_by_pattern(self.location_dir, ExpGroup._GROUP_DIR_PREFIX)
        for num in nums:
            group = ExpGroup._load(self.location_dir, num)
            self._num_to_child[num] = group
            self._name_to_child[group.data.name] = group
        helper._process_status(self)
        return True

    def has_group(self, num_or_name):
        self._update()
        return util._has_in_num_or_name_dicts(num_or_name, self._num_to_child, self._name_to_child)

    def make_group(self, name, descr, num=None) -> ExpGroup:
        self._update()
        util._check_num(num, True)
        if name in self._name_to_child:
            raise ValueError(f"A group with the name `{name}` already exists!")
        if num is not None:
            if num in self._num_to_child:
                raise ValueError(f"A group with the num `{num}` already exists!")
        else:
            num = util._get_highest_num_in_dict(self._num_to_child) + 1
        group = ExpGroup._make(self.location_dir, num, name, descr)
        self._num_to_child[num] = group
        self._name_to_child[name] = group
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
        del self._num_to_child[num]
        del self._name_to_child[name]
        shutil.rmtree(group_dir)

    def group(self, num_or_name) -> ExpGroup:
        self._update()
        return util._get_by_num_or_name(num_or_name, self._num_to_child, self._name_to_child)

    def groups(self):
        self._update()
        return list(self._num_to_child.values())

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

    def start(self):
        self._update()
        pass  # TODO
        #  TODO proj.start() - seeking for the best candidate, or
        #   proj.start(exp_dot_num) - run given exact experiment, e.g. 1.1
