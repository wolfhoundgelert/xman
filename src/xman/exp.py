from .struct import ExpStructData, ExpStruct, ExpStructStatus
from .pipeline import Pipeline
from . import util

import os


class ExpData(ExpStructData):

    def __init__(self, name, descr):
        super().__init__(name, descr)


class ExpStatus(ExpStructStatus):

    def __init__(self, status: str, resolution: str = None):
        super().__init__(status, resolution)

    def _workflow(self):
        return (
            ExpStructStatus.TODO,
            (ExpStructStatus.IN_PROGRESS, ExpStructStatus.IN_PROGRESS_ACTIVE, ExpStructStatus.IN_PROGRESS_NOT_ACTIVE),
            (ExpStructStatus.DONE, ExpStructStatus.ERROR),
            (ExpStructStatus.SUCCESS, ExpStructStatus.FAIL)
        )


class Exp(ExpStruct):

    _EXP_DIR_PREFIX = 'exp'
    _EXP_FILE = 'exp.pkl'

    @staticmethod
    def _get_exp_dir(group_location_dir, num):
        return os.path.join(group_location_dir, Exp._EXP_DIR_PREFIX + str(num))

    @staticmethod
    def _get_exp_file(location_dir):
        return os.path.join(location_dir, Exp._EXP_FILE)

    @staticmethod
    def _make(group_location_dir, num, name, descr):
        location_dir = Exp._get_exp_dir(group_location_dir, num)
        location_dir = util._make_dir(location_dir)
        data = ExpData(name, descr)
        exp = Exp(location_dir, num, data)
        exp._save_data()
        return exp

    @staticmethod
    def _load(group_location_dir, num):
        location_dir = Exp._get_exp_dir(group_location_dir, num)
        data = ExpStruct._load_data(location_dir, Exp._EXP_FILE)
        return Exp(location_dir, num, data)

    def __init__(self, location_dir: str, num: int, data: ExpData):
        super().__init__(location_dir, data)
        util._check_num(num, False)
        self.location_dir = location_dir
        self.num = num
        self.data = data
        self.status = None
        self._update()

    def __str__(self):
        return f"Exp {self.num} [{self.status()}] {self.data.name} - {self.data.descr}"

    def _file_path(self):
        return Exp._get_exp_file(self.location_dir)

    def _update(self):
        if not super()._update():
            return
        ms = self.data.manual_status
        if ms is not None:
            self.status = ms
        else:
            self.status = ExpStatus(ExpStructStatus.TODO)  # TODO infer by other information

    def set_manual_status(self, status: str, resolution: str) -> ExpStatus:
        ms = ExpStatus(status, resolution)
        self.data.manual_status = ms
        self._save_data()
        self._update()
        return ms

    def remove_manual_status(self):
        ms = self.data.manual_status
        self.data.manual_status = None
        self._save_data()
        self._update()

    def run(self):
        pass  # TODO run experiment
        # TODO group.run() - seeking the best candidate for running (IN_PROGRESS_NOT_ACTIVE),
        #  group.run(exp_num) - run given exact experiment, e.g. 1
        #  proj.run() - seeking for the best candidate,
        #  proj.run(exp_dot_num) - run given exact experiment, e.g. 1.1

        # TODO raise error if it has manual status, because it can be processed only manually

    def success(self, resolution: str):
        return self.set_manual_status(ExpStructStatus.SUCCESS, resolution)

    def fail(self, resolution: str):
        return self.set_manual_status(ExpStructStatus.FAIL, resolution)
