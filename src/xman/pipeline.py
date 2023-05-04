import os
from typing import Any, Callable
import time

from .error import get_error_str, get_error_stack_str
from .event import Event, EventDispatcher


class PipelineEvent(Event):

    STARTED = 'STARTED'
    FINISHED = 'FINISHED'
    ERROR = 'ERROR'


class PulseEvent(Event):

    PULSE = 'PULSE'  # TODO Implement
    INTERMEDIATE_CHECKPOINT = 'INTERMEDIATE_CHECKPOINT'  # TODO Implement


# TODO Implement
class Pulse(EventDispatcher):

    _TIMESTAMPS_AMOUNT = 3

    def __init__(self, location_dir):
        self.location_dir = os.path.normpath(location_dir)
        self.intermediate_checkpoints = []
        self._timestamps = []

    # Somewhere in the run_func: call pulse() or pulse(*info for saving, replaced or stacked*)
    def __call__(self, intermediate_checkpoint=None, replace=True):
        if intermediate_checkpoint is not None:
            if replace:
                self.intermediate_checkpoints[0] = intermediate_checkpoint
            else:
                self.intermediate_checkpoints.append(intermediate_checkpoint)
            # TODO Save and dispatch or smth else
        self.__tick()

    # Should be called in run_func via pulse() for letting xman know that's the exp is still alive
    def __tick(self):
        self.timestamps.append(time.time())
        if len(self.timestamps) > Pulse._TIMESTAMPS_AMOUNT:
            self.timestamps = self.timestamps[-Pulse._TIMESTAMPS_AMOUNT:]
        # self.exp._save_and_update()  # TODO Should be an event dispatch


class PipelineData:  # Saved in exp._data.pipeline

    def __init__(self, started, finished, error, error_stack, result, pulse_timestamps):
        self.started = started
        self.finished = finished
        self.error = error
        self.error_stack = error_stack
        self.result = result
        self.pulse_timestamps = pulse_timestamps
        # self.intermediate_checkpoints: [] = intermediate_checkpoints  # TODO Implement it


class PipelineRunData:  # Saved in `.run` file, might be really heavy (several GB)

    def __init__(self, run_func: Callable[[Pulse, ...], Any], params: dict):
        self.run_func = run_func
        self.params = params


class Pipeline(EventDispatcher):

    def __init__(self, location_dir: str, data: PipelineData, run_data: PipelineRunData):
        super().__init__()
        # self.__location_dir = location_dir  # TODO pass to Pulse for saving checkpoints in the same folder with the exp
        self.__data = data
        self.__run_data = run_data
        # self.__pulse = Pulse(exp.location_dir)
        # TODO Add event listener for saving intermediate results

    def __process_error(self, error):
        data = self.__data
        data.error = get_error_str(error)
        data.error_stack = get_error_stack_str(error)

    def _start(self):
        data = self.__data
        run_data = self.__run_data
        data.started = True
        self._dispatch(PipelineEvent, PipelineEvent.STARTED)
        # TODO Pulse operating
        # self.pulse = Pulse(self.exp)
        # self.pulse()
        error = None
        try:
            # data.result = run_data.run_func(self.pulse, **run_data.params) # TODO Temporary None for pulse
            data.result = run_data.run_func(None, **run_data.params)  # TODO Pass self.__pulse
            data.finished = True
            self._dispatch(PipelineEvent, PipelineEvent.FINISHED)
        except Exception as e:
            error = e
            self.__process_error(e)
            self._dispatch(PipelineEvent, PipelineEvent.ERROR)
        if error is not None:
            raise error

    def _destroy(self):
        pass  # TODO Remove pulse, destroy components
        super()._destroy()
