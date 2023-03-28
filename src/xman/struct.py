import os
import pickle


class ExpStructData:

    def __init__(self, name, descr):
        self.name = name
        self.descr = descr


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

    def __str__(self):
        raise NotImplementedError(f"`__str__` method should be overriden!")

    # Printing in jupyter notebook - https://stackoverflow.com/a/41454816/9751954
    def _repr_pretty_(self, p, cycle):
        p.text(str(self) if not cycle else '...')

    def _get_file_path(self):
        raise NotImplementedError(f"`_get_file_path` method should be overriden!")

    def _save_data(self):
        fp = self._get_file_path()

        with open(fp, 'wb') as f:
            pickle.dump(self.data, f)

    def update(self):
        raise NotImplementedError(f"`update` method should be overriden!")