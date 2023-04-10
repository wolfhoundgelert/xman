from .struct import ExpStructData, ExpStruct, ExpStructStatus
from .pipeline import Pipeline


class ExpData(ExpStructData):

    def __init__(self, name, descr):
        super().__init__(name, descr)
        self.pipeline = None
        self.manual_result = None  # TODO implement


class Exp(ExpStruct):

    @staticmethod
    def _dir_prefix():
        return 'exp'

    def __str__(self):
        return f"Exp {self.num} [{self.status()}] {self.data.name} - {self.data.descr}"

    @property
    def _data_class(self):
        return ExpData

    def _update(self):
        super()._update()
        if self.data.manual_status is None:
            resolution = ExpStruct._AUTO_STATUS_RESOLUTION
            pipeline = self.data.pipeline
            if pipeline is None:
                status = ExpStructStatus.EMPTY
            elif not pipeline.started:
                status = ExpStructStatus.TODO
            elif pipeline.error is not None:
                status = ExpStructStatus.ERROR
                resolution = str(pipeline.error)
            elif pipeline.finished:
                status = ExpStructStatus.DONE
            else:
                status = ExpStructStatus.IN_PROGRESS
                # TODO update ACTIVE, IDLE, UNKNOWN type of IN_PROGRESS
            self.status = ExpStructStatus(status, resolution, manual=False)

    def _on_load_data(self, loaded_data):
        loaded_data.pipeline.exp = self  # Because pipeline.exp is another instance after being loaded
        super()._on_load_data(loaded_data)

    def set_manual_result(self, result):
        self._update()
        self.data.manual_result = result
        self._save()

    def remove_manual_result(self):
        self._update()
        self.data.manual_result = None
        self._save()

    def attach_pipeline(self, run_func, params):
        self._update()
        if self.data.pipeline is not None:
            raise AssertionError(f"`{self}` already has a pipeline!")
        pipeline = Pipeline(self, run_func, params)
        self.data.pipeline = pipeline
        self._save()
        return self

    def remove_pipeline(self):
        self._update()
        if self.data.pipeline is not None:
            self.data.pipeline = None
            self._save()
        return self

    def start(self):
        self._update()
        pipeline = self.data.pipeline
        if pipeline is None:
            raise AssertionError(f"`{self}` doesn't have a pipeline!")
        if pipeline.error:
            raise AssertionError(f"`{self}` has an error during the previous start!")
        if pipeline.started:
            raise AssertionError(f"`{self}` was already started and the current status is `{self.status}`!")
        if pipeline.finished:
            raise AssertionError(f"`{self}` was already finished!")
        pipeline._start()

    def success(self, resolution: str):
        self._update()
        self.set_manual_status(ExpStructStatus.SUCCESS, resolution)

    def fail(self, resolution: str):
        self._update()
        self.set_manual_status(ExpStructStatus.FAIL, resolution)

    def info(self):
        self._update()
        super().info()
        if self.status.resolution:
            print(f"    Resolution: {self.status.resolution}")
        if self.result:
            print(f"    Result: {self.result}")

    @property
    def result(self):
        self._update()
        if self.data.manual_result is not None:
            return self.data.manual_result
        if self.data.pipeline is not None:
            return self.data.pipeline.result
        return None

    @property
    def error(self):
        self._update()
        return self.data.pipeline.error if self.data.pipeline else None
