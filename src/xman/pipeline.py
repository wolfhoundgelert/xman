import os
import threading
from pathlib import Path
from threading import Timer
from typing import Any, Callable, Optional, List

from . import filesystem
from .config import PipelineConfig
from .error import get_error_str, get_error_stack_str, NotExistsXManError


class CheckpointsMediator:

    @property
    def exp_location_dir(self): return self.__exp_location_dir

    @property
    def default_checkpoints_dir(self): return self.__default_checkpoints_dir

    def save_checkpoint(self, checkpoint: Any, replace: bool,
                        custom_path: str = None) -> str:
        # TODO Delete work plan or rework it the docs
        """
        + Saves all checkpoints placed inside the exp folder as relative to the folder.

        + If a custom_path was placed outside the exp folder, the path will be saved as it was
        provided.

        + During loading the path will be tried first as a relative to the exp folder, then as it
        is, if source via the relative path doesn't exist.

        + If both paths aren't exist, then NotExist exception will be raised with mentioning of JSON
        file which should be fixed manually or checkpoints folder should be deleted via special
        method.

        + Refine checkpoints on pipeline start

        + Refine checkpoints on getting via mediator's method
        """
        cp_list = self.get_checkpoint_paths_list(check_files_exist=True)
        if replace and cp_list is not None:
            for cp_path in cp_list:
                filesystem.delete_checkpoint(cp_path, self.__exp_location_dir)
            filesystem.delete_checkpoints_list(self.__exp_location_dir)
            cp_list = None
        if not filesystem.has_checkpoints_dir(self.__exp_location_dir):
            filesystem.make_checkpoints_dir(self.__exp_location_dir)
        cp_path = filesystem.save_checkpoint(checkpoint, self.__exp_location_dir, custom_path)
        cp_list = [] if cp_list is None else cp_list
        cp_list.append(cp_path)
        filesystem.save_checkpoints_list(cp_list, self.__exp_location_dir)
        return cp_path if custom_path is None else custom_path

    def get_checkpoint_paths_list(self, check_files_exist: bool = True) -> Optional[List[str]]:
        lst = filesystem.load_checkpoints_list(self.__exp_location_dir)
        if lst is None or not check_files_exist:
            return lst
        missed = []
        for it in lst:
            path = filesystem.resolve_checkpoint_path(it, self.__exp_location_dir)
            if path is None:
                missed.append(it)
        if len(missed):
            json_path = filesystem.get_checkpoints_list_path(self.__exp_location_dir)
            NotExistsXManError(f"Can't resolve some checkpoints paths - {missed}! You can fix paths"
                               f" right in the {json_path} or remove checkpoints via "
                               f"`exp.delete_checkpoints()` method of the experiment structure.")
        return lst

    def load_checkpoint(self, checkpoint_path: str) -> Optional[Any]:
        path = filesystem.resolve_checkpoint_path(checkpoint_path, self.__exp_location_dir)
        if path is None:
            raise NotExistsXManError(f"Can't find checkpoint by the path `{checkpoint_path}`!")
        return filesystem.load_checkpoint(path)

    def __init__(self, exp_location_dir: str):
        self.__exp_location_dir = exp_location_dir
        self.__default_checkpoints_dir = filesystem.get_checkpoints_dir_path(exp_location_dir)
        # Check checkpoints are ok (paths can be lost during files or folders moving:
        self.get_checkpoint_paths_list(check_files_exist=True)


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
        self.__do_timestamp()
        try:
            if run_data.with_mediator:
                self.__mediator = CheckpointsMediator(self.__location_dir)
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
