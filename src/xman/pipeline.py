import os
from typing import Any, Callable
import time

from . import filesystem, maker
from .error import get_error_str, get_error_stack_str
from .event import Event, EventDispatcher


class PulseEvent(Event):

    PULSE = 'PULSE'
    INTERMEDIATE_CHECKPOINT = 'INTERMEDIATE_CHECKPOINT'


class Pulse(EventDispatcher):

    _TIMESTAMPS_AMOUNT = 3

    def __init__(self, location_dir: str, intermediate_checkpoints: []):
        super().__init__()
        self.location_dir = os.path.normpath(location_dir)
        self.intermediate_checkpoints = intermediate_checkpoints
        self._timestamps = []

    # Somewhere in the run_func: call pulse() or pulse(info_for_saving, replaced_or_stacked)
    def __call__(self, intermediate_checkpoint=None, replace=True):
        if intermediate_checkpoint is not None:
            if replace:
                self.intermediate_checkpoints.clear()
            self.intermediate_checkpoints.append(intermediate_checkpoint)
            super()._dispatch(PulseEvent, PulseEvent.INTERMEDIATE_CHECKPOINT)
        self.__tick()

    # Should be called in run_func via pulse() for letting `xman` know that's the exp is still alive
    def __tick(self):
        self._timestamps.append(time.time())
        if len(self._timestamps) > Pulse._TIMESTAMPS_AMOUNT:
            self._timestamps = self._timestamps[-Pulse._TIMESTAMPS_AMOUNT:]
        super()._dispatch(PulseEvent, PulseEvent.PULSE)

    def _destroy(self):
        self._timestamps.clear()
        self._timestamps = None
        self.intermediate_checkpoints.clear()
        self.intermediate_checkpoints = None
        super()._destroy()


class PipelineData:  # Saved in exp._data.pipeline

    def __init__(self, started, finished, error, error_stack, result, pulse_timestamps):
        self.started = started
        self.finished = finished
        self.error = error
        self.error_stack = error_stack
        self.result = result
        self.pulse_timestamps = pulse_timestamps


class PipelineRunData:  # Saved in `.run` file, might be really heavy (several GB)

    def __init__(self, run_func: Callable[[Pulse, ...], Any], params: dict):
        self.run_func = run_func
        self.params = params


class PipelineEvent(Event):

    STARTED = 'STARTED'
    FINISHED = 'FINISHED'
    ERROR = 'ERROR'
    PULSE = 'PULSE'


class Pipeline(EventDispatcher):

    def __init__(self, location_dir: str, data: PipelineData, run_data: PipelineRunData):
        super().__init__()
        self.__location_dir = os.path.normpath(location_dir)
        self.__data = data
        self.__run_data = run_data
        self.__pulse = None

    def __process_error(self, error):
        data = self.__data
        data.error = get_error_str(error)
        data.error_stack = get_error_stack_str(error)

    def _start(self):
        data = self.__data
        run_data = self.__run_data
        data.started = True
        self.__pulse = maker._make_pulse(self.__location_dir)
        self.__pulse._add_listener(PulseEvent, self.__pulse_listener)
        self.__pulse()  # for saving the first timestamp on start
        self._dispatch(PipelineEvent, PipelineEvent.STARTED)
        error = None
        try:
            data.result = run_data.run_func(self.__pulse, **run_data.params)
            data.finished = True
            self._dispatch(PipelineEvent, PipelineEvent.FINISHED)
        except Exception as e:
            error = e
            self.__process_error(e)
            self._dispatch(PipelineEvent, PipelineEvent.ERROR)
        if error is not None:
            raise error

    def _destroy(self):
        if self.__pulse is not None:
            self.__pulse._remove_listener(PulseEvent, self.__pulse_listener)
        maker._destroy_pulse(self.__pulse, self.__location_dir)
        self.__pulse = None
        super()._destroy()

    def __pulse_listener(self, event: PulseEvent):
        if event.kind == PulseEvent.PULSE:
            self.__data.pulse_timestamps = self.__pulse._timestamps
            self._dispatch(PipelineEvent, PipelineEvent.PULSE)
        elif event.kind == PulseEvent.INTERMEDIATE_CHECKPOINT:
            pulse: Pulse = event.target
            filesystem._save_checkpoint(pulse.intermediate_checkpoints, self.__location_dir)
