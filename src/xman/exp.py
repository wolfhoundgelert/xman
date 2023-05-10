import time
from typing import Any, Optional

from .error import NotExistsXManError, IllegalOperationXManError
from .pipeline import PipelineData, PipelineEvent
from .struct import ExpStructData, ExpStruct, ExpStructStatus
from . import util, confirm
from . import maker


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

    @property
    def _state(self):
        return self.__state

    @property
    def _idle(self):
        return self._manual or self._status.status != ExpStructStatus.IN_PROGRESS \
            or self._state == ExpState.IDLE

    @property
    def _result(self) -> Optional[Any]:
        if self._data.manual_result is not None:
            return self._data.manual_result
        if self._data.pipeline is not None:
            return self._data.pipeline.result
        return None

    @property
    def _error(self) -> Optional[str]:
        return None if self._data.pipeline is None else self._data.pipeline.error

    @property
    def _error_stack(self) -> Optional[str]:
        return None if self._data.pipeline is None else self._data.pipeline.error_stack

    def _make_pipeline(self, run_func, params, save=False) -> 'Exp':
        self.__check_not_manual()
        self.__pipeline = maker._make_pipeline(self, run_func, params, save)
        self.__pipeline._add_listener(PipelineEvent, self.__pipeline_listener)
        self._save_and_update()
        return self

    def _destroy_pipeline(self, need_confirm=True) -> Optional['Exp']:
        if not self.__check_not_active():
            return None
        if self._data.pipeline is None:
            raise NotExistsXManError(f"There's no pipeline in exp `{self}`!")
        if confirm._request(need_confirm, f"ATTENTION! Remove the pipeline of exp `{self}`?"):
            self.__destroy_pipeline(False, True)
            return self
        return None

    def _start(self) -> 'Exp':
        self.__check_not_manual()
        pipeline_data = self._data.pipeline
        if pipeline_data is None:
            raise NotExistsXManError(f"`{self}` doesn't have a pipeline!")
        if pipeline_data.error:
            raise IllegalOperationXManError(f"`{self}` has an error during the previous start!")
        if pipeline_data.started:
            raise IllegalOperationXManError(
                f"`{self}` was already started and the current status is `{self._status}`!")
        if pipeline_data.finished:
            raise IllegalOperationXManError(f"`{self}` was already finished!")
        if self.__pipeline is None:
            self.__pipeline = maker._recreate_pipeline(self)
        try:
            self.__pipeline._start()
        finally:
            self.__destroy_pipeline(True, True)
        return self

    def _set_manual_result(self, result, need_confirm=True) -> Optional['Exp']:
        if self._data.manual_result is not None:
            if not confirm._request(need_confirm,
                                    f"Do you want to rewrite the previous result of the exp `{self}`?"):
                return None
        self._data.manual_result = result
        self._save_and_update()
        return self

    def _delete_manual_result(self, need_confirm=True) -> Optional['Exp']:
        if self._data.manual_result is None:
            raise NotExistsXManError(f"There's no manual result in exp `{self}`!")
        if confirm._request(need_confirm, f"ATTENTION! Remove the manual result of exp `{self}`?"):
            self._data.manual_result = None
            self._save_and_update()
            return self
        return None

    def _success(self, resolution: str) -> Optional['Exp']:
        self._set_manual_status(ExpStructStatus.SUCCESS, resolution)
        return self

    def _fail(self, resolution: str) -> Optional['Exp']:
        self._set_manual_status(ExpStructStatus.FAIL, resolution)
        return self

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
        if self._manual:
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
                    state = ExpState.ACTIVE if elapsed < max(1.5 * average, 10 * util.SECOND) \
                        else ExpState.IDLE
                elif average < util.HOUR:
                    state = ExpState.ACTIVE if elapsed < max(1.1 * average, 2 * util.MINUTE) \
                        else ExpState.IDLE
                else:
                    state = ExpState.ACTIVE if elapsed < max(1.05 * average, 5 * util.MINUTE) \
                        else ExpState.IDLE
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

    def _set_manual_status(self, status: str, resolution: str) -> Optional['Exp']:
        if not self.__check_not_active():
            return None
        return super()._set_manual_status(status, resolution)

    def _info(self):
        text = super()._info()
        if self._result is not None:
            text += util.tab(f"\nResult:\n{util.tab(str(self._result))}")
        return text

    def _destroy(self):
        if not self._idle:
            raise IllegalOperationXManError(f"Exp `{self}` might be in progress right now!")
        self.__destroy_pipeline(False, False)
        self._data.manual_result = None
        super()._destroy()

    def __init__(self, location_dir):
        self.__state = None
        self.__pipeline = None
        self.__updating = False
        super().__init__(location_dir)

    def __str__(self):
        state = f": {self._state}" if self._status == ExpStructStatus.IN_PROGRESS else ''
        return f"Exp {self.num} [{self._status}{state}] {self._data.name} - {self._data.descr}"

    def __check_not_manual(self):
        if self._manual:
            raise IllegalOperationXManError(f"Illegal operation for manual experiments! "
                f"Delete manual status first: `delete_manual_status()`.")

    def __check_not_active(self):
        if self._state == ExpState.ACTIVE:
            raise IllegalOperationXManError(f"Can't proceed while the exp is active "
                                            f"(has a pipeline that is executing right now!")
        if not self._manual and self._status == ExpStructStatus.IN_PROGRESS:
            if not util.response(f"Exp is in `{self._state}` state. "
                                 f"Are you sure you want to proceed?"):
                return False
        return True

    def __destroy_pipeline(self, keep_data: bool, save_and_update):
        if self.__pipeline is not None:
            self.__pipeline._remove_listener(PipelineEvent, self.__pipeline_listener)
        maker._destroy_pipeline(self, self.__pipeline, keep_data)
        self.__pipeline = None
        if save_and_update:
            self._save_and_update()

    def __pipeline_listener(self, event: PipelineEvent): self._save_and_update()
