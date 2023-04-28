import time

from . import util
from .pipeline import Pipeline
from .struct import ExpStructData, ExpStruct, ExpStructStatus


class ExpData(ExpStructData):

    def __init__(self, name, descr):
        super().__init__(name, descr)
        self.pipeline = None
        self.manual_result = None


class ExpState:

    IDLE = 'IDLE'
    ACTIVE = 'ACTIVE'
    UNKNOWN = 'UNKNOWN'


class ExpConfig:

    UNKNOWN_TO_IDLE_TIME = 8 * util.HOUR
    ACTIVE_FROM_START = 60 * util.SECOND


class Exp(ExpStruct):

    @staticmethod
    def _dir_prefix(): return 'exp'

    def __init__(self, location_dir, name, descr):
        self.__state = None
        self.__updating = False
        super().__init__(location_dir, name, descr)

    def __str__(self):
        state = f": {self._state}" if self._status == ExpStructStatus.IN_PROGRESS else ''
        return f"Exp {self.num} [{self._status}{state}] {self._data.name} - {self._data.descr}"

    @property
    def _data_class(self): return ExpData

    @property
    def _state(self): return self.__state

    def _process_auto_status(self):
        resolution = ExpStruct._AUTO_STATUS_RESOLUTION
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
        return status, resolution

    def _update_state(self):
        manual = self._data.manual_status is not None
        if manual:
            state = ExpState.UNKNOWN
        elif self._status != ExpStructStatus.IN_PROGRESS:
            state = ExpState.IDLE
        else:
            state = ExpState.UNKNOWN
            timestamps = self._data.pipeline.pulse.timestamps
            t = time.time()
            elapsed = t - timestamps[-1]
            ts_len = len(timestamps)
            if ts_len > 1:
                average = (timestamps[-1] - timestamps[0]) / (ts_len - 1)
                # TODO ??? Simplify with one config param?
                if average < util.SECOND:
                    state = ExpState.ACTIVE if elapsed < 10 * util.SECOND else ExpState.IDLE
                elif average < util.MINUTE:
                    state = ExpState.ACTIVE if elapsed < max(1.5 * average, 10 * util.SECOND) else ExpState.IDLE
                elif average < util.HOUR:
                    state = ExpState.ACTIVE if elapsed < max(1.1 * average, 2 * util.MINUTE) else ExpState.IDLE
                else:
                    state = ExpState.ACTIVE if elapsed < max(1.05 * average, 5 * util.MINUTE) else ExpState.IDLE
            else:
                if elapsed < ExpConfig.ACTIVE_FROM_START:
                    state = ExpState.ACTIVE
            if state == ExpState.UNKNOWN:
                if elapsed > ExpConfig.UNKNOWN_TO_IDLE_TIME:
                    state = ExpState.IDLE
        self.__state = state

    def _update(self):
        if self.__updating:
            return
        self.__updating = True
        super()._update()
        # Status and state should be updated at the end of the inherited updating hierarchy
        if type(self) == Exp:
            self._update_status()
            self._update_state()
        self.__updating = False

    def _on_load_data(self, loaded_data):
        if loaded_data.pipeline is not None:
            loaded_data.pipeline.exp = self  # Because pipeline.exp is another instance after being loaded
        super()._on_load_data(loaded_data)

    def _info(self):
        text = super()._info()
        if self.result is not None:
            text += util.tab(f"\nResult:\n{util.tab(str(self.result))}")
        return text

    def set_manual_result(self, result, confirm=True):
        self._update()
        if self._data.manual_result is not None:
            if confirm and not util.response(f"Do you want to rewrite the previous result of the exp `{self}`?"):
                return None
        self._data.manual_result = result
        self._save_and_update()
        return self

    def delete_manual_result(self, confirm=True):
        self._update()
        if self._data.manual_result is None:
            raise AssertionError(f"There's no manual result in exp `{self}`!")
        if not confirm or util.response(f"ACHTUNG! Remove the manual result of exp `{self}`?"):
            self._data.manual_result = None
            self._save_and_update()
            return self
        return None

    def make_pipeline(self, run_func, params):
        self._update()
        if self._data.pipeline is not None:
            raise AssertionError(f"`{self}` already has a pipeline!")
        pipeline = Pipeline(self, run_func, params)
        self._data.pipeline = pipeline
        self._save_and_update()
        return self

    def destroy_pipeline(self, confirm=True):
        self._update()
        if self._data.pipeline is None:
            raise AssertionError(f"There's no pipeline in exp `{self}`!")
        if not confirm or util.response(f"ACHTUNG! Remove the pipeline of exp `{self}`?"):
            self._data.pipeline = None
            self._save_and_update()
            return self
        return None

    def start(self):
        self._update()
        pipeline = self._data.pipeline
        if pipeline is None:
            raise AssertionError(f"`{self}` doesn't have a pipeline!")
        if pipeline.error:
            raise AssertionError(f"`{self}` has an error during the previous start!")
        if pipeline.started:
            raise AssertionError(f"`{self}` was already started and the current status is `{self._status}`!")
        if pipeline.finished:
            raise AssertionError(f"`{self}` was already finished!")
        pipeline._start()

    def success(self, resolution: str):
        self._update()
        self.set_manual_status(ExpStructStatus.SUCCESS, resolution)
        return self

    def fail(self, resolution: str):
        self._update()
        self.set_manual_status(ExpStructStatus.FAIL, resolution)
        return self

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
