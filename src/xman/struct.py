from .tree import _print_dir_tree

import os
import pickle
import time


class ExpStructData:

    def __init__(self, name, descr):
        self.name = name
        self.descr = descr
        self.manual_status = None


class ExpStructStatus:

    TODO = 'TODO'
    IN_PROGRESS = 'IN_PROGRESS'
    IN_PROGRESS_ACTIVE = 'IN_PROGRESS_ACTIVE'
    IN_PROGRESS_NOT_ACTIVE = 'IN_PROGRESS_NOT_ACTIVE'
    DONE = 'DONE'
    ERROR = 'ERROR'
    SUCCESS = 'SUCCESS'
    FAIL = 'FAIL'

    @staticmethod
    def __has_workflow_status(workflow, status):
        for it in workflow:
            if it == status:
                return True
            if type(it) is tuple:
                if ExpStructStatus.__has_workflow_status(it, status):
                    return True
        return False

    def __init__(self, status: str, resolution: str = None):
        self.workflow = self._workflow()
        self.__check(status, resolution)
        self.current = status
        self.next = self.__next()
        self.resolution = resolution

    def __str__(self):
        return self.current

    def __call__(self):
        return self.current

    def __check(self, status, resolution):
        if not ExpStructStatus.__has_workflow_status(self.workflow, status):
            raise ValueError(f"The workflow `{self.workflow}` doesn't have status `{status}`!")
        if status in (ExpStructStatus.SUCCESS, ExpStructStatus.FAIL) and resolution is None:
            raise ValueError(f"SUCCESS and FAIL manual statuses require setting resolutions!")

    def __next(self):
        if self.workflow[-1] == self.current:
            return None
        for i, it in enumerate(self.workflow[:-1]):
            if it == self.current or (type(it) is tuple and self.current in it):
                return self.workflow[i + 1]

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle):
        p.text(str(self) if not cycle else '...')

    def _workflow(self):
        raise NotImplementedError(f"`workflow` method should be overriden!")


class ExpStruct:

    @staticmethod
    def _load_data(location_dir, filename):
        fp = os.path.join(location_dir, filename)
        with open(fp, 'rb') as f:
            data = pickle.load(f)
            return data

    def __init__(self, location_dir, data):
        self.location_dir = location_dir
        self.data = data
        self.status = None
        self.__last_update = -1

    def __str__(self):
        raise NotImplementedError(f"`__str__` method should be overriden!")

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle):
        p.text(str(self) if not cycle else '...')

    def _file_path(self):
        raise NotImplementedError(f"`_get_file_path` method should be overriden!")

    def _save_data(self):
        fp = self._file_path()

        with open(fp, 'wb') as f:
            pickle.dump(self.data, f)

    def _update(self):
        t = time.time()
        if t - self.__last_update < 1:
            return False
        self.__last_update = t
        return True

    def print_tree(self):
        self._update()
        _print_dir_tree(self.location_dir)
