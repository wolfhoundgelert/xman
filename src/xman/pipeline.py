from typing import Any, Callable

import time


class Pulse:

    _TIMESTAMPS_AMOUNT = 3

    def __init__(self, exp):
        self.exp = exp
        self.intermediate_checkpoints = []
        self.timestamps = []

    # Somewhere in the run_func: call pulse() or pulse(*info for saving, replaced or stacked*)
    def __call__(self, intermediate_checkpoint=None, replace=True):
        if intermediate_checkpoint is not None:
            if replace:
                self.intermediate_checkpoints[0] = intermediate_checkpoint
            else:
                self.intermediate_checkpoints.append(intermediate_checkpoint)
        self.__tick()

    # Should be called in run_func via pulse() for letting xman know that's the exp is still alive
    def __tick(self):
        self.timestamps.append(time.time())
        if len(self.timestamps) > Pulse._TIMESTAMPS_AMOUNT:
            self.timestamps = self.timestamps[-Pulse._TIMESTAMPS_AMOUNT:]
        self.exp._save()


class Pipeline:

    # TODO Will it be more convenient to require users to inherit Pipeline instead of passing run_func?
    def __init__(self, exp, run_func: Callable[[Pulse, ...], Any], params: dict):
        self.exp = exp
        self.run_func = run_func
        self.params = params
        self.result = None
        self.pulse = None
        self.started = False
        self.finished = False
        self.error = None

    def _start(self):
        self.started = True
        self.pulse = Pulse(self.exp)
        self.pulse()
        try:
            self.result = self.run_func(self.pulse, **self.params)
            self.finished = True
        except Exception as err:
            self.error = err
        self.exp._save()
