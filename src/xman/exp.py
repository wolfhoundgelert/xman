import time

from . import util
from .pipeline import Pipeline
from .struct import ExpStructData, ExpStruct, ExpStructStatus


class ExpData(ExpStructData):

    def __init__(self, name, descr):
        super().__init__(name, descr)
        self.pipeline = None
        self.manual_result = None


class InProgressType:

    ACTIVE = 'ACTIVE'
    IDLE = 'IDLE'
    UNKNOWN = 'UNKNOWN'


class ExpStatus(ExpStructStatus):

    def __init__(self, status: str, resolution: str = None, manual: bool = False, in_progress_type: str = None):
        super().__init__(status, resolution, manual)
        self.in_progress_type = in_progress_type

    def __str__(self):
        if self.manual:
            return self.status + ' *'
        if self.status == ExpStructStatus.IN_PROGRESS:
            return self.status + f': {self.in_progress_type}'
        return self.status


class ExpConfig:

    UNKNOWN_TO_IDLE_TIME = 8 * util.HOUR
    ACTIVE_FROM_START = 60 * util.SECOND


class Exp(ExpStruct):

    @staticmethod
    def _dir_prefix():
        return 'exp'

    def __str__(self):
        return f"Exp {self.num} [{self.status()}] {self._data.name} - {self._data.descr}"

    def __process_in_progress_type(self):
        in_progress_type = InProgressType.UNKNOWN
        timestamps = self._data.pipeline.pulse.timestamps
        t = time.time()
        elapsed = t - timestamps[-1]
        ts_len = len(timestamps)
        if ts_len > 1:
            average = (timestamps[-1] - timestamps[0]) / (ts_len - 1)
            # TODO ??? Simplify with one config param?
            if average < util.SECOND:
                in_progress_type = InProgressType.ACTIVE if elapsed < 10 * util.SECOND else InProgressType.IDLE
            elif average < util.MINUTE:
                in_progress_type = InProgressType.ACTIVE if elapsed < max(1.5 * average,
                                                                          10 * util.SECOND) else InProgressType.IDLE
            elif average < util.HOUR:
                in_progress_type = InProgressType.ACTIVE if elapsed < max(1.1 * average,
                                                                          2 * util.MINUTE) else InProgressType.IDLE
            else:
                in_progress_type = InProgressType.ACTIVE if elapsed < max(1.05 * average,
                                                                          5 * util.MINUTE) else InProgressType.IDLE
        else:
            if elapsed < ExpConfig.ACTIVE_FROM_START:
                in_progress_type = InProgressType.ACTIVE
        if in_progress_type == InProgressType.UNKNOWN:
            if elapsed > ExpConfig.UNKNOWN_TO_IDLE_TIME:
                in_progress_type = InProgressType.IDLE
        return in_progress_type

    @property
    def _data_class(self):
        return ExpData

    def _update(self):
        super()._update()
        if self._data.manual_status is None:
            resolution = ExpStruct._AUTO_STATUS_RESOLUTION
            in_progress_type = None
            pipeline = self._data.pipeline
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
                in_progress_type = self.__process_in_progress_type()
            self.status = ExpStatus(status, resolution, manual=False, in_progress_type=in_progress_type)

    def _on_load_data(self, loaded_data):
        if loaded_data.pipeline is not None:
            loaded_data.pipeline.exp = self  # Because pipeline.exp is another instance after being loaded
        super()._on_load_data(loaded_data)

    def set_manual_result(self, result):
        self._update()
        self._data.manual_result = result  # TODO Add guard for keeping the previous result
        self._save()

    def remove_manual_result(self):
        self._update()
        self._data.manual_result = None
        self._save()

    def make_pipeline(self, run_func, params):
        self._update()
        if self._data.pipeline is not None:
            raise AssertionError(f"`{self}` already has a pipeline!")
        pipeline = Pipeline(self, run_func, params)
        self._data.pipeline = pipeline
        self._save()
        return self

    def remove_pipeline(self):
        self._update()
        if self._data.pipeline is not None:
            self._data.pipeline = None
            self._save()
        return self

    def start(self):
        self._update()
        pipeline = self._data.pipeline
        if pipeline is None:
            raise AssertionError(f"`{self}` doesn't have a pipeline!")
        if pipeline.error:
            raise AssertionError(f"`{self}` has an error during the previous start!")
        if pipeline.started:
            raise AssertionError(f"`{self}` was already started and the current status is `{self.status}`!")
        if pipeline.finished:
            raise AssertionError(f"`{self}` was already finished!")
        pipeline._start()

    def success(self, resolution: str):
        self._update()
        self.set_manual_status(ExpStructStatus.SUCCESS, resolution)

    def fail(self, resolution: str):
        self._update()
        self.set_manual_status(ExpStructStatus.FAIL, resolution)

    def info(self):
        self._update()
        super().info()
        spaces = '    '
        if self.status.resolution:
            print(f"{spaces}Resolution: {self.status.resolution}")
        if self.result:
            result = str(self.result).replace('\n', f"\n{spaces * 2}")
            print(f"{spaces}Result:\n{spaces * 2}{result}")

    @property
    def result(self):
        self._update()
        if self._data.manual_result is not None:
            return self._data.manual_result
        if self._data.pipeline is not None:
            return self._data.pipeline.result
        return None

    @property
    def error(self):
        self._update()
        return self._data.pipeline.error if self._data.pipeline else None
