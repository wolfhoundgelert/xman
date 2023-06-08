from typing import Any, List

from . import catalog
from . import filesystem as fs


class Note:

    @property
    def txt(self) -> str:
        return catalog.load_note(self.__location_dir, fs.FileType.TXT)

    @txt.setter
    def txt(self, obj: Any):
        file_type = fs.FileType.TXT
        catalog.delete_note(self.__location_dir, file_type) if obj is None \
            else catalog.save_note(self.__location_dir, obj, file_type)

    @property
    def json(self) -> Any:
        return catalog.load_note(self.__location_dir, fs.FileType.JSON)

    @json.setter
    def json(self, obj: Any):
        file_type = fs.FileType.JSON
        catalog.delete_note(self.__location_dir, file_type) if obj is None \
            else catalog.save_note(self.__location_dir, obj, file_type)

    @property
    def pickle(self) -> Any: return catalog.load_note(self.__location_dir, fs.FileType.PICKLE)

    @pickle.setter
    def pickle(self, obj: Any):
        file_type = fs.FileType.PICKLE
        catalog.delete_note(self.__location_dir, file_type) if obj is None \
            else catalog.save_note(self.__location_dir, obj, file_type)

    @property
    def has_any(self):
        for file_type in fs.FileType:
            path = catalog.get_note_path(self.__location_dir, file_type)
            if catalog.has(path):
                return True
        return False

    def get_list(self) -> List[str]:
        result = []
        for file_type in fs.FileType:
            path = catalog.get_note_path(self.__location_dir, file_type)
            if catalog.has(path):
                result.append(path)
        return result

    def get_existence_str(self) -> str:
        result = ''
        for file_type in fs.FileType:
            path = catalog.get_note_path(self.__location_dir, file_type)
            result += f"{file_type.name} {catalog.has(path)}, "
        return result.removesuffix(', ').lower()

    def clear(self):
        catalog.delete_note(self.__location_dir, fs.FileType.TXT)
        catalog.delete_note(self.__location_dir, fs.FileType.JSON)
        catalog.delete_note(self.__location_dir, fs.FileType.PICKLE)

    def __init__(self, location_dir: str): self.__location_dir = location_dir

    def __str__(self): return str(self.get_list())

    def __call__(self, *args, **kwargs): print(self)
