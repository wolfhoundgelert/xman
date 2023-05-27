from typing import Any, List, Optional

from . import filesystem


class Note:

    @property
    def txt(self) -> str:
        return filesystem.load_note(self.__location_dir, filesystem.FileType.TXT)

    @txt.setter
    def txt(self, obj: Any):
        file_type = filesystem.FileType.TXT
        filesystem.delete_note(self.__location_dir, file_type) if obj is None \
            else filesystem.save_note(obj, self.__location_dir, file_type)

    @property
    def json(self) -> Any:
        return filesystem.load_note(self.__location_dir, filesystem.FileType.JSON)

    @json.setter
    def json(self, obj: Any):
        file_type = filesystem.FileType.JSON
        filesystem.delete_note(self.__location_dir, file_type) if obj is None \
            else filesystem.save_note(obj, self.__location_dir, file_type)

    @property
    def pickle(self) -> Any:
        return filesystem.load_note(self.__location_dir, filesystem.FileType.PICKLE)

    @pickle.setter
    def pickle(self, obj: Any):
        file_type = filesystem.FileType.PICKLE
        filesystem.delete_note(self.__location_dir, file_type) if obj is None \
            else filesystem.save_note(obj, self.__location_dir, file_type)

    @property
    def has_any(self):
        for file_type in filesystem.FileType:
            path = filesystem.get_note_path(self.__location_dir, file_type)
            if filesystem.has(path):
                return True
        return False

    def get_list(self) -> List[str]:
        result = []
        for file_type in filesystem.FileType:
            path = filesystem.get_note_path(self.__location_dir, file_type)
            if filesystem.has(path):
                result.append(path)
        return result

    def get_existence_str(self) -> str:
        result = ''
        for file_type in filesystem.FileType:
            path = filesystem.get_note_path(self.__location_dir, file_type)
            result += f"{file_type.name} {filesystem.has(path)}, "
        return result.removesuffix(', ').lower()

    def clear(self):
        filesystem.delete_note(self.__location_dir, filesystem.FileType.TXT)
        filesystem.delete_note(self.__location_dir, filesystem.FileType.JSON)
        filesystem.delete_note(self.__location_dir, filesystem.FileType.PICKLE)

    def __init__(self, location_dir: str): self.__location_dir = location_dir

    def __str__(self): return str(self.get_list())

    def __call__(self, *args, **kwargs): print(self)
