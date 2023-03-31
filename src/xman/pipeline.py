from typing import Any, Callable


class Pipeline:

    def __init__(self, func: Callable[..., Any], params: dict):
        self.func = func
        self.params = params
        self.result = None
        # self.__called = False  # TODO ??? in self.run() check it was called before

    def run(self):
        # TODO try-catch, return status object or PipelineResult
        self.result = self.func(**self.params)
        return self.result