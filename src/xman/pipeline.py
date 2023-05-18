import os
import threading
from threading import Timer
from typing import Any, Callable, Optional, List

from . import filesystem
from .config import PipelineConfig
from .error import get_error_str, get_error_stack_str


class CheckpointsMediator:

    @property
    def exp_location_dir(self):
        return self.__exp_location_dir

    @property
    def default_checkpoints_dir(self):
        return self.__default_checkpoints_dir

    def save_checkpoint(self, checkpoint: Any, replace: bool,
                        custom_path: str = None) -> str:
        cp_list = self.get_checkpoint_paths_list()
        if replace and cp_list is not None:
            for cp_path in cp_list:
                filesystem.delete_checkpoint(cp_path)
            filesystem.delete_checkpoints_list(self.__exp_location_dir)
            cp_list = None
        if not filesystem.has_checkpoints_dir(self.__exp_location_dir):
            filesystem.make_checkpoints_dir(self.__exp_location_dir)
        cp_path = filesystem.save_checkpoint(checkpoint, self.__exp_location_dir, custom_path)
        cp_list = [] if cp_list is None else cp_list
        cp_list.append(cp_path)
        filesystem.save_checkpoints_list(cp_list, self.__exp_location_dir)
        return cp_path

    def get_checkpoint_paths_list(self) -> Optional[List[str]]:
        return filesystem.load_checkpoints_list(self.__exp_location_dir)

    def load_checkpoint(self, checkpoint_path) -> Optional[Any]:
        return filesystem.load_checkpoint(checkpoint_path)

    def __init__(self, exp_location_dir: str):
        self.__exp_location_dir = exp_location_dir
        self.__default_checkpoints_dir = filesystem.get_checkpoints_dir_path(exp_location_dir)


class PipelineData:  # Saved in exp._data.pipeline

    def __init__(self):
        self.started: bool = False
        self.finished: bool = False
        self.error: str = None
        self.error_stack: str = None
        self.result: Any = None


class PipelineRunData:  # Saved in `.run` file, might be really heavy (several GB)

    def __init__(self, run_func: Callable[..., Any] | Callable[[CheckpointsMediator, ...], Any],
                 with_mediator: bool, params: dict):
        self.run_func = run_func
        self.with_mediator = with_mediator
        self.params = params


class Pipeline:

    def start(self):
        data = self.__data
        run_data = self.__run_data
        data.started = True
        error = None
        if run_data.with_mediator:
            self.__mediator = CheckpointsMediator(self.__location_dir)
        self.__do_timestamp()
        try:
            if run_data.with_mediator:
                data.result = run_data.run_func(self.__mediator, **run_data.params)
            else:
                data.result = run_data.run_func(**run_data.params)
            data.finished = True
        except Exception as e:
            error = e
            self.__process_error(e)
        if error is not None:
            raise error

    def _destroy(self):
        if self.__timer is not None:
            self.__timer.cancel()
            self.__timer = None
        if self.__mediator is not None:
            self.__mediator = None
        self.__data = None
        self.__run_data = None

    def __init__(self, location_dir: str, data: PipelineData, run_data: PipelineRunData):
        self.__location_dir = os.path.normpath(location_dir)
        self.__data = data
        self.__run_data = run_data
        self.__mediator: CheckpointsMediator = None
        self.__timer: Timer = None

    def __process_error(self, error):
        data = self.__data
        data.error = get_error_str(error)
        data.error_stack = get_error_stack_str(error)

    def __do_timestamp(self):
        filesystem.save_run_timestamp(self.__location_dir)
        self.__timer = threading.Timer(PipelineConfig.timer_interval, self.__do_timestamp)
