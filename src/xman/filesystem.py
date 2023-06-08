import json
import os
import shutil
import time
from enum import Enum
from typing import Optional, Any
import cloudpickle as pickle  # dill as pickle, cloudpickle as pickle, pickle

from xman import confirm


__file_path_to_mtime = {}
__file_path_to_content = {}


class FileType(Enum):

    TXT = '.txt'
    JSON = '.json'
    PICKLE = '.pickle'


# TODO `load` rename to `get`


def __get_cached_mtime(file_path): return __file_path_to_mtime[file_path]


def __exists_in_cache(file_path): return file_path in __file_path_to_mtime


def __save_to_cache(file_path, content):
    __file_path_to_mtime[file_path] = get_mtime(file_path)
    __file_path_to_content[file_path] = content


def __load_from_cache(file_path): return __file_path_to_content[file_path]


def __delete_cache(file_path):
    __file_path_to_mtime.pop(file_path, None)
    __file_path_to_content.pop(file_path, None)


def __save_to_file(file_path, file_type, content):
    make_dir(os.path.dirname(file_path))
    if file_type is FileType.TXT:
        with open(file_path, 'w') as f:
            f.write(str(content))
    if file_type is FileType.JSON:
        with open(file_path, 'w') as f:
            json.dump(content, f, indent=4)
    if file_type is FileType.PICKLE:
        with open(file_path, 'wb') as f:
            pickle.dump(content, f)


def __load_from_file(file_path, file_type) -> Optional[Any]:
    if file_type is FileType.TXT:
        with open(file_path, 'r') as f:
            return f.read()
    if file_type is FileType.JSON:
        with open(file_path, 'r') as f:
            return json.load(f)
    if file_type is FileType.PICKLE:
        with open(file_path, 'rb') as f:
            return pickle.load(f)


def __delete_file(file_path):
    if exists(file_path):
        os.remove(file_path)


# TODO Check it's used only by `catalog.py`
def exists(path: str) -> bool: return os.path.exists(path)


def get_mtime(file_path): return os.path.getmtime(file_path)


def save(file_path: str, file_type: FileType, content: Any):
    if exists(file_path) and get_mtime(file_path) == time.time():
        time.sleep(1e-3)
    __save_to_file(file_path, file_type, content)
    __save_to_cache(file_path, content)


def load(file_path: str, file_type: FileType) -> Optional[Any]:
    if not exists(file_path):
        __delete_cache(file_path)
        return None
    if __exists_in_cache(file_path) and __get_cached_mtime(file_path) == get_mtime(file_path):
        return __load_from_cache(file_path)
    content = __load_from_file(file_path, file_type)
    __save_to_cache(file_path, content)
    return content


def delete(file_path: str):
    __delete_file(file_path)
    __delete_cache(file_path)
    
    
def make_dir(dir_path, exist_ok=True): os.makedirs(dir_path, exist_ok=exist_ok)


def delete_dir(dir_path: str, need_confirm: bool = True) -> bool:
    if not exists(dir_path):
        return True
    if len(os.listdir(dir_path)) > 0 and not confirm.request(
            need_confirm, f"ATTENTION! Dir `{dir_path}`\nisn't empty - delete anyway?"):
        return False
    for folder_path, _, file_names in os.walk(dir_path):
        for file_name in file_names:
            file_path = os.path.join(folder_path, file_name)
            __delete_cache(file_path)
    shutil.rmtree(dir_path, ignore_errors=True)
    return True


def rename_or_move_dir(dir_path, new_path): shutil.move(dir_path, new_path)
