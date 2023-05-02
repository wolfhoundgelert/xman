import time

from . import util
from .error import NotExistsXManError, AlreadyExistsXManError, IllegalOperationXManError
from .pipeline import PipelineData, PipelineRunData, Pipeline, PipelineEvent
from .struct import ExpStructData, ExpStruct, ExpStructStatus


class ExpData(ExpStructData):

    def __init__(self, name, descr):
        super().__init__(name, descr)
        self.pipeline: PipelineData = None
        self.manual_result = None


class ExpState:

    IDLE = 'IDLE'
    ACTIVE = 'ACTIVE'
    UNKNOWN = 'UNKNOWN'


class ExpConfig:

    UNKNOWN_TO_IDLE_TIME = 8 * util.HOUR
    ACTIVE_FROM_START = 60 * util.SECOND


class Exp(ExpStruct):

    __RUN_FILE = '.run'

    @staticmethod
    def _dir_prefix(): return 'exp'

    def __init__(self, location_dir, name, descr):
        self.__state = None
        self.__pipeline = None
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
        pipeline_data = self._data.pipeline
        if pipeline_data is None:
            status = ExpStructStatus.EMPTY
        elif not pipeline_data.started:
            status = ExpStructStatus.TODO
        elif pipeline_data.error is not None:
            status = ExpStructStatus.ERROR
            resolution = str(pipeline_data.error)
        elif pipeline_data.finished:
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

    def _info(self):
        text = super()._info()
        if self.result is not None:
            text += util.tab(f"\nResult:\n{util.tab(str(self.result))}")
        return text

    def _PipelineEvent_listener(self, event: PipelineEvent): self._save_and_update()

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
            raise NotExistsXManError(f"There's no manual result in exp `{self}`!")
        if not confirm or util.response(f"ACHTUNG! Remove the manual result of exp `{self}`?"):
            self._data.manual_result = None
            self._save_and_update()
            return self
        return None

    def make_pipeline(self, run_func, params, save=False):
        self._update()
        if self._data.pipeline is not None:
            raise AlreadyExistsXManError(f"`{self}` already has a pipeline!")
        pipeline_data = PipelineData(False, False, None, None, None, None)
        self._data.pipeline = pipeline_data
        pipeline_run_data = PipelineRunData(run_func, params, None)
        if save:
            util.save(pipeline_run_data, self.location_dir, Exp.__RUN_FILE)
        self.__pipeline = Pipeline(self.location_dir, pipeline_data, pipeline_run_data)
        self.__pipeline._add_listener(PipelineEvent, self._PipelineEvent_listener)
        self._save_and_update()
        return self

    def destroy_pipeline(self, confirm=True):
        self._update()
        if self._data.pipeline is None:
            raise NotExistsXManError(f"There's no pipeline in exp `{self}`!")
        if not confirm or util.response(f"ACHTUNG! Remove the pipeline of exp `{self}`?"):
            if self.__pipeline is not None:
                self.__pipeline._remove_listener(PipelineEvent, self._PipelineEvent_listener)
                self.__pipeline._destroy()
                self.__pipeline == None
            self._data.pipeline = None
            self._save_and_update()
            return self
        return None

    def start(self):
        self._update()
        pipeline_data = self._data.pipeline
        if pipeline_data is None:
            raise NotExistsXManError(f"`{self}` doesn't have a pipeline!")
        if pipeline_data.error:
            raise IllegalOperationXManError(f"`{self}` has an error during the previous start!")
        if pipeline_data.started:
            raise IllegalOperationXManError(f"`{self}` was already started and the current status is `{self._status}`!")
        if pipeline_data.finished:
            raise IllegalOperationXManError(f"`{self}` was already finished!")
        self.__pipeline._start()

    # TODO Need to check that exp isn't run from another acc, check other places
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
