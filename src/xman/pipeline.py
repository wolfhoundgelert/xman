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

    def interim_result(self):
        pass  # TODO


class Pipeline:

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
            raise AssertionError(f"Pipeline is already started!")
        self.started = True
        # TODO save `started` flag to exp.data
        self.pulse = Pulse(self)  # TODO unchain cycle linking Pipeline <-> Pulse
        # TODO add try-catch and return status object or PipelineResult
        try:
            self.result = self.run_func(self.pulse, **self.params)
        except Exception as err:
            self.error = err
            # TODO save `error` flag to exp.data
        self.finished = True
        # TODO save `finished` flag to exp.data
