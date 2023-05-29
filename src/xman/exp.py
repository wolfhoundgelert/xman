import time
from typing import Any, Optional, Callable

from .config import PipelineConfig
from .error import NotExistsXManError, IllegalOperationXManError, AlreadyExistsXManError, \
    UnpredictableLogicXManError, NothingToDoXManError
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

    # Is 'IN_PROGRESS' status and executing right now ( + some buffer for the lag on Colab platform)
    ACTIVE = 'ACTIVE'

    # Any experiments except not manual in `IN_PROGRESS` status and is executing right now.
    IDLE = 'IDLE'


class Exp(ExpStruct):

    @property
    def group(self) -> 'ExpGroup': return self.parent

    @property
    def proj(self) -> 'ExpProj': return self.parent.parent

    @property
    def state(self) -> str: return self.__state

    @property
    def result(self) -> Optional[Any]:
        manual_result = self._data.manual_result
        pipeline_result = None if self._data.pipeline is None else self._data.pipeline.result
        if manual_result is not None and pipeline_result is not None:
            raise IllegalOperationXManError(f"There are two results in the `{self}` - manual result"
                                            f" and pipeline result! Use `get_manual_result()` or "
                                            f"`get_pipeline_result()` for checking them and delete "
                                            f"manual result or pipeline.")
        return pipeline_result if manual_result is None else manual_result

    @property
    def error(self) -> Optional[str]:
        return None if self._data.pipeline is None else self._data.pipeline.error

    @property
    def error_stack(self) -> Optional[str]:
        return None if self._data.pipeline is None else self._data.pipeline.error_stack

    @property
    def is_active(self) -> bool: return self.state == ExpState.ACTIVE

    @property
    def is_ready_for_start(self) -> bool:
        if self.is_manual:
            return False
        return (self.status.status_str == ExpStructStatus.IN_PROGRESS and
                self.state == ExpState.IDLE) or self.status.status_str == ExpStructStatus.TO_DO

    @property
    def checkpoints_mediator(self) -> CheckpointsMediator:
        if self.__checkpoints_mediator is None:
            self.__checkpoints_mediator = CheckpointsMediator(self.location_dir)
        return self.__checkpoints_mediator

    def info(self):
        text = super().info()
        if self.result is not None:
            text += util.tab(f"\nResult:\n{util.tab(self.view_result())}")
        return text

    def view_result(self) -> str:
        rv = self.result_viewer
        if rv is None and self.parent is not None:
            rv = self.parent.result_viewer
            if rv is None and self.parent.parent is not None:
                rv = self.parent.parent.result_viewer
        return str(self.result) if rv is None else rv(self.result)

    def make_pipeline(self, run_func: Callable[..., Any],
                      params: dict, save_on_storage: bool = False) -> 'Exp':
        return self.__make_pipeline(run_func, False, params, save_on_storage)

    def make_pipeline_with_checkpoints(self,
                               run_func_with_mediator: Callable[[CheckpointsMediator, ...], Any],
                               params: dict, save_on_storage: bool = False) -> 'Exp':
        return self.__make_pipeline(run_func_with_mediator, True, params, save_on_storage)

    def delete_pipeline(self, need_confirm: bool = True) -> Optional['Exp']:
        self._check_is_not_active()
        if self._data.pipeline is None:
            raise NotExistsXManError(f"There's no pipeline in exp `{self}`!")
        if confirm.request(need_confirm, f"ATTENTION! Remove the pipeline of exp `{self}` "
                                          f"(it will also delete all checkpoints and all pipeline"
                                          f"data)?"):
            maker.delete_pipeline(self, self.__pipeline)
            self.__pipeline = None
            self._save()
            return self
        return None

    def delete_checkpoints(self, need_confirm: bool = True, delete_custom_paths: bool = False)\
            -> Optional['Exp']:
        self._check_is_not_active()
        if not confirm.request(need_confirm, f"ATTENTION! Do you want to delete `{self}` "
                                              f"checkpoints?"):
            return None
        if delete_custom_paths:
            lst = self.checkpoints_mediator.get_checkpoint_paths_list(check_files_exist=True)
            if lst is not None:
                for cp_path in lst:
                    filesystem.delete_checkpoint(cp_path, self.location_dir)
        filesystem.delete_checkpoints_dir(self.location_dir, need_confirm=False)
        return self

    def start(self) -> 'Exp':
        if self._data.manual_result is not None:
            raise IllegalOperationXManError(f"The `{self}` already has a manual result - delete it "
                                            f"with `delete_manual_result()` method first!")
        if self.is_ready_for_start:
            if filesystem.has_checkpoints_dir(self.location_dir) and \
                    self.status.status_str == ExpStructStatus.TO_DO:
                raise IllegalOperationXManError(f"`{self}` contains checkpoints folder - delete it "
                                                f"first with `delete_checkpoints()` method!")
            if self.__pipeline is None:
                self.__pipeline = maker.recreate_pipeline(self)
            try:
                self.__pipeline.start()
            finally:
                self._save()
                self.__pipeline._destroy()
                self.__pipeline = None
                filesystem.delete_pipeline_run_data(self.location_dir)
                filesystem.delete_run_timestamp(self.location_dir)
        else:
            self._check_is_not_active()
            if self.is_manual:
                raise IllegalOperationXManError(f"Can't start the `{self}` as it's manual - use "
                                                f"`delete_manual_status()` method first!")
            pipeline_data = self._data.pipeline
            if pipeline_data is None:  # status == 'EMPTY'
                raise NotExistsXManError(f"`The {self}` doesn't have a pipeline!")
            if pipeline_data.error:  # status == 'ERROR'
                raise IllegalOperationXManError(
                    f"The `{self}` has an error during the previous start!")
            if pipeline_data.finished:  # status == 'DONE'
                raise IllegalOperationXManError(f"`The {self}` was already finished!")
        return self

    def get_pipeline_result(self) -> Optional[Any]:
        if self._data.pipeline is None:
            raise IllegalOperationXManError(f"There's no pipeline in the `{self}`!")
        return self._data.pipeline.result

    def set_manual_result(self, result: Any) -> 'Exp':
        if self._data.manual_result is not None:
            raise AlreadyExistsXManError(f"Already has a manual result!")
        self._data.manual_result = result
        self._save()
        return self

    def get_manual_result(self) -> Optional[Any]:
        if self._data.manual_result is None:
            raise IllegalOperationXManError(f"There's no manual result in the `{self}`!")
        return self._data.manual_result

    def delete_manual_result(self, need_confirm: bool = True) -> Optional['Exp']:
        if self._data.manual_result is None:
            raise NotExistsXManError(f"There's no manual result in the `{self}`!")
        if not confirm.request(need_confirm, f"ATTENTION! The manual result for the `{self} will "
                                              f"be deleted - proceed?"):
            return None
        self._data.manual_result = None
        self._save()
        return self

    def delete_all_manual(self, need_confirm: bool = True) -> Optional['Exp']:
        if not self.is_manual and not self._data.manual_result:
            raise NothingToDoXManError(f"There's nothing manual to delete!")
        if not confirm.request(need_confirm, f"ATTENTION! Manual status and resolution, and manual"
                                             f"result will be deleted - proceed?"):
            return None
        self._data.manual_status = None
        self._data.manual_status_resolution = None
        self._data.manual_result = None
        self._save()
        return self

    def clear(self, need_confirm: bool = True) -> Optional['Exp']:
        self._check_is_not_active()
        if not confirm.request(need_confirm,
                                f"ATTENTION! The `{self}` will be cleared as it just was "
                                f"created - proceed?"):
            return None
        if self._data.pipeline is not None:
            self.delete_pipeline(need_confirm=False)
        self.delete_checkpoints(need_confirm=False, delete_custom_paths=True)
        self.__checkpoints_mediator = None
        self._data.manual_result = None
        self._data.manual_status = None
        self._data.manual_status_resolution = None
        self.result_viewer = None
        self.note.clear()
        self.__note = None
        self._save()
        return self

    def update(self):
        if self.__updating:
            return
        self.__updating = True
        super().update()
        # Status and state should be updated at the end of the inherited updating hierarchy
        if type(self) == Exp:
            self._update_status()
            self.__update_state()
        self.__updating = False

    def _process_auto_status(self):
        resolution = ExpStruct._AUTO_STATUS_RESOLUTION
        pipeline_data = self._data.pipeline
        if pipeline_data is None:
            status = ExpStructStatus.EMPTY
        elif not pipeline_data.started:
            status = ExpStructStatus.TO_DO
        elif pipeline_data.error is not None:
            status = ExpStructStatus.ERROR
            resolution = str(pipeline_data.error)
        elif pipeline_data.finished:
            status = ExpStructStatus.DONE
        else:
            status = ExpStructStatus.IN_PROGRESS
        return status, resolution

    def _check_is_not_active(self):
        if self.is_active:
            raise IllegalOperationXManError(f"Illegal operation while the experiment is active - "
                                            f"has a pipeline that is executing right now!")

    def _destroy(self):
        if self.__pipeline is not None:
            if self.is_active:
                raise UnpredictableLogicXManError(f"It shouldn't be, but if you're reading this... "
                        f"So, something extraordinary has happened - congrats and my condolences!)")
            self.__pipeline._destroy()
        self._data.manual_result = None
        self.__checkpoints_mediator = None
        super()._destroy()

    def __init__(self, location_dir, parent):
        from .api import ExpAPI
        self._data: ExpData = None
        self.__state = None
        self.__pipeline: Pipeline = None
        self.__checkpoints_mediator = None
        self.__updating = False
        super().__init__(location_dir, parent)
        self._api = ExpAPI(self)

    def __str__(self):
        state = f": {self.state}" if self.status.status_str == ExpStructStatus.IN_PROGRESS else ''
        return f"Exp {self.num} [{self.status}{state}] {self._data.name} - {self._data.descr}"

    def __is_active_by_time_delta(self):
        run_timestamp = filesystem.load_run_timestamp(self.location_dir)
        if run_timestamp is None:
            return False
        active_buffer = PipelineConfig.active_buffer_colab if platform.is_colab \
            else PipelineConfig.active_buffer
        return time.time() - run_timestamp < PipelineConfig.timer_interval + active_buffer

    def __is_active(self):
        p_data = self._data.pipeline
        return p_data is not None and p_data.started and not p_data.finished and \
            p_data.error is None and self.__is_active_by_time_delta()

    def __update_state(self):
        self.__state = ExpState.ACTIVE if self.__is_active() else ExpState.IDLE

    def __make_pipeline(self, run_func, with_mediator, params, save_on_storage):
        if self._data.pipeline is not None:
            raise AlreadyExistsXManError(f"`{self}` already has a pipeline!")
        self.__pipeline = maker.make_pipeline(self, run_func, with_mediator, params,
                                              save_on_storage)
        self._save()
        return self
