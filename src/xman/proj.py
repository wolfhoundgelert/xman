from .struct import ExpStructData, ExpStruct
from . import util

import os


class ExperimentalProjectData(ExpStructData):

    def __init__(self, name, descr):
        super().__init__(name, descr)


class ExperimentalProject(ExpStruct):

    _PROJ_FILE = 'exp_proj.pkl'

    @staticmethod
    def __get_proj_file(location_dir):
        return os.path.join(location_dir, ExperimentalProject._PROJ_FILE)

    @staticmethod
    def _create(location_dir, name, descr):
        location_dir = util._create_dir(location_dir)
        data = ExperimentalProjectData(name, descr)
        proj = ExperimentalProject(location_dir, data)
        proj._save_data()
        return proj

    @staticmethod
    def _load(location_dir):
        data = ExpStruct._load_data(location_dir, ExperimentalProject._PROJ_FILE)
        return ExperimentalProject(location_dir, data)

    def __int__(self, location_dir, data):
        super().__init__(location_dir, data)
        self.__num_to_group = None
        self.__name_to_group = None
        self.update()

    def __str__(self):
        # TODO investigate why doesn't work as self.__num_to_group.values()
        gl = [str(it) for it in self.__num_to_group.values()]
        return f"Experimental project: name `{self.data.name}`, descr `{self.data.descr}`, status `{self.status}`, groups {gl}"

    def _get_file_path(self):
        return ExperimentalProject.__get_proj_file(self.location_dir)

    # TODO add last changes timestamp for the whole project or exact section and compare the version
    #  (don't need to update if they are equals)
    def update(self):
        self.__num_to_group = {}
        self.__name_to_group = {}
        print('updated')
        # nums = util._get_dir_nums_by_pattern(self.location_dir, ExperimentGroup._GROUP_DIR_PREFIX)
        #
        # for num in nums:
        #     group = ExperimentGroup._load(self.location_dir, num)
        #     self.__num_to_group[num] = group
        #     self.__name_to_group[group.data.name] = group

        self.status = None  # TODO depends on exp groups statuses, which depends on exp statuses
