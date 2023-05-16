import time
from typing import Any, Optional, Callable

from .config import PipelineConfig
from .error import NotExistsXManError, IllegalOperationXManError, AlreadyExistsXManError
from .pipeline import PipelineData, CheckpointsMediator, Pipeline
from .struct import ExpStructData, ExpStruct, ExpStructStatus
from . import util, confirm, platform, filesystem
from . import maker


class ExpData(ExpStructData):

    def __init__(self, name, descr):
        super().__init__(name, descr)
        self.pipeline: PipelineData = None
        self.manual_result: Any = None


class ExpState:

    # Any experiments except not manual in `IN_PROGRESS` status and is executing right now.
    IDLE = 'IDLE'

    # Is 'IN_PROGRESS' status and executing right now ( + some buffer for the lag on Colab platform)
    ACTIVE = 'ACTIVE'


class Exp(ExpStruct):

    @property
    def _state(self): return self.__state

    @property
    def _result(self) -> Optional[Any]:
        manual_result = self._data.manual_result
        pipeline_result = None if self._data.pipeline is None else self._data.pipeline.result
        if manual_result is not None and pipeline_result is not None:
            raise IllegalOperationXManError(f"There are two results in the `{self}` - manual result"
                                            f" and pipeline result! Use `get_manual_result()` or "
                                            f"`get_pipeline_result()` instead.")
        return pipeline_result if manual_result is None else manual_result

    @property
    def _error(self) -> Optional[str]:
        return None if self._data.pipeline is None else self._data.pipeline.error

    @property
    def _error_stack(self) -> Optional[str]:
        return None if self._data.pipeline is None else self._data.pipeline.error_stack

    def _info(self):
        text = super()._info()
        if self._result is not None:
            text += util.tab(f"\nResult:\n{util.tab(str(self._result))}")
        return text

    def _make_pipeline(self, run_func: Callable[..., Any], params, save_on_storage=False) -> 'Exp':
        return self.__make_pipeline(run_func, False, params, save_on_storage)

    def _make_pipeline_with_checkpoints(self,
                                        run_func_with_mediator: Callable[[CheckpointsMediator, ...], Any],
                                        params: dict, save_on_storage: bool = False) -> 'Exp':
        return self.__make_pipeline(run_func_with_mediator, True, params, save_on_storage)

    def _destroy_pipeline(self, need_confirm=True) -> Optional['Exp']:
        self.__check_not_active()
        if self._data.pipeline is None:
            raise NotExistsXManError(f"There's no pipeline in exp `{self}`!")
        if confirm._request(need_confirm, f"ATTENTION! Remove the pipeline of exp `{self}` "
                                          f"(it will also delete all checkpoints and all pipeline"
                                          f"data)?"):
            self.__destroy_pipeline(keep_data=False, need_save=True)
            return self
        return None

    def _get_checkpoints_mediator(self): return CheckpointsMediator(self._location_dir)

    def _delete_checkpoints(self, need_confirm=True, delete_custom_paths=False) -> Optional['Exp']:
        self.__check_not_active()
        if not confirm._request(need_confirm, f"ATTENTION! Do you want to delete `{self}` "
                                              f"checkpoints?"):
            return None
        if delete_custom_paths:
            cp_list = filesystem._load_checkpoints_list(self._location_dir)
            if cp_list is not None:
                for cp_path in cp_list:
                    filesystem._delete_checkpoint(cp_path)
        filesystem._delete_checkpoints_dir(self._location_dir)
        return self

    def _is_ready_for_start(self):
        if self._is_manual:
            return False
        return (self._status == ExpStructStatus.IN_PROGRESS and self._state == ExpState.IDLE) \
            or self._status == ExpStructStatus.TODO

    def _start(self) -> 'Exp':
        self.__check_not_active()
        if filesystem._has_checkpoints_dir(self._location_dir):
            raise IllegalOperationXManError(f"`{self}` contains checkpoints folder - delete it "
                                            f"first with `delete_checkpoints()` method!")
        pipeline_data = self._data.pipeline
        if pipeline_data is None:  # status == 'EMPTY'
            raise NotExistsXManError(f"`{self}` doesn't have a pipeline!")
        if pipeline_data.error:  # status == 'ERROR'
            raise IllegalOperationXManError(f"`{self}` has an error during the previous start!")
        if pipeline_data.finished:  # status == 'DONE'
            raise IllegalOperationXManError(f"`{self}` was already finished!")
        # status == 'TODO_' here, or 'IN_PROGRESS' with state 'IDLE'
        if self.__pipeline is None:
            self.__pipeline = maker._recreate_pipeline(self)
        try:
            self.__pipeline._start()
        finally:
            self.__destroy_pipeline(keep_data=True, need_save=True)
        return self

    def _get_pipeline_result(self) -> Optional[Any]:
        if self._data.pipeline is None:
            raise IllegalOperationXManError(f"There's no pipeline in the `{self}`!")
        return self._data.pipeline.result

    def _set_manual_result(self, result) -> 'Exp':
        if self._data.manual_result is not None:
            raise AlreadyExistsXManError(f"Already has a manual result!")
        self._data.manual_result = result
        self._save()
        return self

    def _get_manual_result(self) -> Optional[Any]:
        if self._data.result is None:
            raise IllegalOperationXManError(f"There's no manual result in the `{self}`!")
        return self._data.manual_result

    def _delete_manual_result(self) -> 'Exp':
        if self._data.manual_result is None:
            raise NotExistsXManError(f"There's no manual result in the `{self}`!")
        self._data.manual_result = None
        self._save()
        return self

    def _clear(self, need_confirm=True) -> Optional['Exp']:
        self.__check_not_active()
        if not confirm._request(need_confirm,
                                f"ATTENTION! The `{self}` will be cleared as it just was "
                                f"created - proceed?"):
            return None
        self.__destroy_pipeline(keep_data=False, need_save=False)
        self._delete_checkpoints(need_confirm=False, delete_custom_paths=True)
        self._data.manual_result = None
        self._data.manual_status = None
        self._data.manual_status_resolution = None
        self._save()
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

    def _update(self):
        if self.__updating:
            return
        self.__updating = True
        super()._update()
        # Status and state should be updated at the end of the inherited updating hierarchy
        if type(self) == Exp:
            self._update_status()
            self.__update_state()
        self.__updating = False

    def _destroy(self):
        self.__check_not_active()
        self.__destroy_pipeline(keep_data=False, need_save=False)
        self._data.manual_result = None
        super()._destroy()

    def __init__(self, location_dir, parent):
        self._data: ExpData = None
        self.__state = None
        self.__pipeline: Pipeline = None
        self.__updating = False
        super().__init__(location_dir, parent)

    def __str__(self):
        state = f": {self._state}" if self._status == ExpStructStatus.IN_PROGRESS else ''
        return f"Exp {self._num} [{self._status}{state}] {self._data.name} - {self._data.descr}"

    def __is_active_by_time_delta(self):
        run_timestamp = filesystem._load_run_time(self._location_dir)
        if run_timestamp is None:
            return False
        active_buffer = PipelineConfig.active_buffer_colab if platform.is_colab \
            else PipelineConfig.active_buffer
        return time.time() - run_timestamp < PipelineConfig.timer_interval + active_buffer

    def __is_active(self):
        pl = self._data.pipeline
        return pl is not None and pl.started and not pl.finished and pl.error is None \
            and self.__is_active_by_time_delta()

    def __update_state(self):
        self.__state = ExpState.ACTIVE if self.__is_active() else ExpState.IDLE

    def __check_not_active(self) -> bool:
        if self._state == ExpState.ACTIVE:
            raise IllegalOperationXManError(f"Illegal operation while the experiment is active "
                                            f"(has a pipeline that is executing right now)!")

    def __make_pipeline(self, run_func, with_mediator, params, save):
        if self._data.pipeline is not None:
            raise AlreadyExistsXManError(f"`{self}` already has a pipeline!")
        self.__pipeline = maker._make_pipeline(self, run_func, with_mediator, params, save)
        self._save()
        return self

    def __destroy_pipeline(self, keep_data: bool, need_save: bool):
        maker._destroy_pipeline(self, self.__pipeline, keep_data)
        self.__pipeline = None
        if need_save:
            self._save()
