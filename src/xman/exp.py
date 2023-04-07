from .struct import ExpStructData, ExpStruct, ExpStructStatus
from .pipeline import Pipeline
from . import util
from . import helper

import os


class ExpData(ExpStructData):

    def __init__(self, name, descr):
        super().__init__(name, descr)
        self.pipeline = None
        self.result = None


class Exp(ExpStruct):

    _EXP_DIR_PREFIX = 'exp'

    @staticmethod
    def _get_exp_dir(group_location_dir, num):
        return os.path.join(group_location_dir, Exp._EXP_DIR_PREFIX + str(num))

    @staticmethod
    def _make(group_location_dir, num, name, descr):
        util._check_num(num, False)
        location_dir = Exp._get_exp_dir(group_location_dir, num)
        return ExpStruct._make(ExpData, Exp, location_dir, name, descr)

    @staticmethod
    def _load(group_location_dir, num):
        util._check_num(num, False)
        location_dir = Exp._get_exp_dir(group_location_dir, num)
        return ExpStruct._load(Exp, location_dir)

    def __str__(self):
        return f"Exp {self.num} [{self.status()}] {self.data.name} - {self.data.descr}"

    def _update(self):
        if not super()._update():
            return False
        util.debug(f"Exp.update()")  # TODO remove debug
        if self.data.manual_status is not None:
            status = self.data.manual_status
            resolution = self.data.manual_status_resolution
            manual = True
        else:
            resolution = helper._AUTO_STATUS_RESOLUTION
            manual = False
            pipeline = self.data.pipeline
            if pipeline is None:
                status = ExpStructStatus.EMPTY
            elif not pipeline.started:
                status = ExpStructStatus.TODO
            elif pipeline.error is not None:
                status = ExpStructStatus.ERROR
                resolution = str(pipeline.error)
            elif pipeline.finished:
                status = ExpStructStatus.DONE
            else:
                status = ExpStructStatus.IN_PROGRESS
                # TODO update ACTIVE, IDLE, UNKNOWN type of IN_PROGRESS
        self.status = ExpStructStatus(status, resolution, manual)
        return True

    # TODO ??? move to ExpStruct, so it will be available for ExpGroup and ExpProj
    def set_manual_status(self, status: str, resolution: str):
        self._update()
        self.status = ExpStructStatus(status, resolution)
        self.data.manual_status = status
        self.data.manual_status_resolution = resolution
        self._save()

    # TODO ??? move to ExpStruct, so it will be available for ExpGroup and ExpProj
    def remove_manual_status(self):
        self._update()
        if self.data.manual_status is None:
            raise AssertionError(f"`{self}` doesn't have a manual status!")
        self.data.manual_status = None
        self.data.manual_status_resolution = None
        self._save()

    def attach_pipeline(self, run_func, params):
        self._update()
        if self.data.pipeline is not None:
            raise AssertionError(f"`{self}` already has a pipeline!")
        pipeline = Pipeline(self, run_func, params)
        self.data.pipeline = pipeline
        self._save()
        return self

    def remove_pipeline(self):
        self._update()
        if self.data.pipeline is not None:
            self.data.pipeline = None
            self.data.result = None
            self._save()
        return self

    def start(self):
        self._update()
        pipeline = self.data.pipeline
        if pipeline is None:
            raise AssertionError(f"`{self}` doesn't have a pipeline!")
        if pipeline.error:
            raise AssertionError(f"`{self}` there's an error during the previous start!")
        if pipeline.started:
            raise AssertionError(f"`{self}` was already started and the current status is `{self.status}`!")
        if pipeline.finished:
            raise AssertionError(f"`{self}` was already finished!")
        pipeline.start()

    def success(self, resolution: str):
        self._update()
        self.set_manual_status(ExpStructStatus.SUCCESS, resolution)

    def fail(self, resolution: str):
        self._update()
        self.set_manual_status(ExpStructStatus.FAIL, resolution)

    def info(self):
        self._update()
        super().info()
        if self.status.resolution:
            print(f"    Resolution: {self.status.resolution}")
        if self.result:
            print(f"    Result: {self.result}")

    # TODO Check how these props should work in case of manual exp
    @property
    def result(self):
        self._update()
        return self.data.pipeline.result if self.data.pipeline else None

    @property
    def error(self):
        self._update()
        return self.data.pipeline.error if self.data.pipeline else None
