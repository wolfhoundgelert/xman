# from .exp import Exp

from typing import Any, Callable


class Pulse:

    def __init__(self, pipeline):
        self.pipeline = pipeline  # TODO check if it's needed
        pass  # TODO

    # TODO should be called in run_func for letting xman know that's the exp is still alive
    def tick(self):
        # TODO save the sequence of timestamps (limit the length, e.g. 10)
        pass  # TODO

    #  TODO save intermediate result and implement resuming mechanics (from the last epoch e.g.)
    def interim_result(self):
        pass  # TODO


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

    def start(self):
        if self.started:
            raise AssertionError(f"Pipeline was already started!")
        self.started = True
        self.pulse = Pulse(self)  # TODO ??? unchain cycle linking Pipeline <-> Pulse
        self.exp._save()
        try:
            self.finished = True
            self.result = self.run_func(self.pulse, **self.params)
        except Exception as err:
            self.error = err
        self.exp._save()
