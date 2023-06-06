import json
import os
import shutil
import time
import re
from enum import Enum
from pathlib import Path
from typing import Optional, Any
import cloudpickle as pickle  # dill as pickle, cloudpickle as pickle, pickle

from .error import ArgumentsXManError, IllegalOperationXManError, NotImplementedXManError, \
    NotExistsXManError
from . import util, maker, confirm


class FileType(Enum):

    TXT = '.txt'
    JSON = '.json'
    PICKLE = '.pickle'


def make_dir(dir_path, exist_ok=True): os.makedirs(dir_path, exist_ok=exist_ok)


def delete_dir(dir_path, need_confirm=True) -> bool:
    if has(dir_path) and len(os.listdir(dir_path)) > 0 and not confirm.request(
            need_confirm, f"ATTENTION! Dir `{dir_path}`\nisn't empty - delete anyway?"):
        return False
    shutil.rmtree(dir_path, ignore_errors=True)
    return True


def rename_or_move_dir(dir_path, new_path): shutil.move(dir_path, new_path)


def __get_data_path(location_dir): return os.path.join(location_dir, '.data')
def __get_time_path(location_dir): return os.path.join(location_dir, '.time')


def get_manual_result_path(location_dir): return os.path.join(location_dir, '.manual_result')


def __get_run_path(location_dir): return os.path.join(location_dir, '.run')
def __get_run_time_path(location_dir): return os.path.join(location_dir, '.run_time')


def get_pipeline_result_path(location_dir): return os.path.join(location_dir, '.pipeline_result')


def get_checkpoints_dir_path(location_dir): return os.path.join(location_dir, 'checkpoints/')


def get_checkpoints_list_path(location_dir):
    return os.path.join(get_checkpoints_dir_path(location_dir), 'list.json')


def __get_checkpoint_path(location_dir):
    current_time_ns = time.time_ns()
    current_time_s = current_time_ns // 10 ** 9  # Convert nanoseconds to seconds
    formatted_time = time.strftime("%Y-%m-%d__%H_%M_%S", time.gmtime(current_time_s))
    fname = formatted_time + '--' + str(current_time_ns)[-9:] + '.cp'
    return os.path.join(get_checkpoints_dir_path(location_dir), fname)


def get_note_path(location_dir, file_type: FileType):
    return os.path.join(location_dir, 'note' + file_type.value)


def get_dir_num(dir_path):
    match = re.search(r'[1-9][0-9]*$', dir_path)
    return int(match.group()) if match else None


def change_num_in_path_by_pattern(path, pattern, new_num) -> str:
    return re.sub(fr'\b{pattern}[1-9][0-9]*\b', f'{pattern}{new_num}', path)


def change_exp_num_in_path(path: str, new_exp_num: int) -> str:
    return change_num_in_path_by_pattern(path, 'exp', new_exp_num)


def change_group_num_in_path(path: str, new_group_num: int) -> str:
    return change_num_in_path_by_pattern(path, 'group', new_group_num)


def __get_dir_nums_by_pattern(dir_path, dir_pattern):
    regex = fr'^{dir_pattern}([1-9][0-9]*)$'
    names = os.listdir(dir_path)
    dirs = [x for x in names if os.path.isdir(os.path.join(dir_path, x))]
    nums = []
    for it in dirs:
        match = re.match(regex, it)
        if match:
            nums.append(int(match.group(1)))
    nums.sort()
    return nums


def dir_prefix(struct_obj_or_cls):
    from .exp import Exp
    from .group import ExpGroup
    from .proj import ExpProj
    cls = util.get_cls(struct_obj_or_cls)
    if cls == Exp:
        return 'exp'
    elif cls == ExpGroup:
        return 'group'
    elif cls == ExpProj:
        raise NotImplementedXManError(f"Isn't supported by logic!")
    else:
        raise ArgumentsXManError(
            f"`struct_obj_or_cls` should be an instance of/or a final class inheriting ExpStruct - "
            f"Exp, ExpGroup or ExpProj, but `{cls.__name__}` was given!")


def get_child_dir(parent, child_num):
    return os.path.join(parent.location_dir, dir_prefix(maker.get_child_class(parent)) +
                        str(child_num))


def get_children_nums(parent):
    child_class = maker.get_child_class(parent)
    child_dir_prefix = dir_prefix(child_class)
    return __get_dir_nums_by_pattern(parent.location_dir, child_dir_prefix)


def has(path) -> bool: return os.path.exists(path)


def prepare_dir(dir_path):
    if has(dir_path):
        if not os.path.isdir(dir_path):
            raise ArgumentsXManError(f"`{dir_path}` is not a directory!")
        elif len(os.listdir(dir_path)) > 0:
            raise IllegalOperationXManError(f"Directory `{dir_path}` should be empty!")
    else:
        make_dir(dir_path)


def __save_to_file(obj, file_path, file_type: FileType):
    make_dir(os.path.dirname(file_path))
    if file_type is FileType.TXT:
        with open(file_path, 'w') as f:
            f.write(str(obj))
    if file_type is FileType.JSON:
        with open(file_path, 'w') as f:
            json.dump(obj, f, indent=4)
    if file_type is FileType.PICKLE:
        with open(file_path, 'wb') as f:
            pickle.dump(obj, f)


def __load_from_file(file_path, file_type: FileType) -> Optional[Any]:
    if has(file_path):
        if file_type is FileType.TXT:
            with open(file_path, 'r') as f:
                return f.read()
        if file_type is FileType.JSON:
            with open(file_path, 'r') as f:
                return json.load(f)
        if file_type is FileType.PICKLE:
            with open(file_path, 'rb') as f:
                return pickle.load(f)
    return None


def __delete_file(file_path):
    if has(file_path):
        os.remove(file_path)


def save_data_and_time(location_dir, data) -> float:
    __save_to_file(data, __get_data_path(location_dir), FileType.PICKLE)
    t = time.time()
    __save_to_file(t, __get_time_path(location_dir), FileType.PICKLE)
    return t


def load_fresh_data_and_time(location_dir, last_data, last_time):
    t = __load_from_file(__get_time_path(location_dir), FileType.PICKLE)
    if last_time != t:
        return __load_from_file(__get_data_path(location_dir), FileType.PICKLE), t
    return last_data, last_time


def save_manual_result(location_dir, manual_result):
    __save_to_file(manual_result, get_manual_result_path(location_dir), file_type=FileType.PICKLE)


def load_manual_result(location_dir):
    return __load_from_file(get_manual_result_path(location_dir), file_type=FileType.PICKLE)


def delete_manual_result(location_dir): __delete_file(get_manual_result_path(location_dir))


def save_pipeline_run_data(location_dir, run_data):
    __save_to_file(run_data, __get_run_path(location_dir), FileType.PICKLE)


def load_pipeline_run_data(location_dir):
    return __load_from_file(__get_run_path(location_dir), FileType.PICKLE)


def delete_pipeline_run_data(location_dir): __delete_file(__get_run_path(location_dir))


def save_pipeline_run_timestamp(location_dir):
    __save_to_file(time.time(), __get_run_time_path(location_dir), FileType.PICKLE)


def load_pipeline_run_timestamp(location_dir):
    return __load_from_file(__get_run_time_path(location_dir), FileType.PICKLE)


def delete_pipeline_run_timestamp(location_dir): __delete_file(__get_run_time_path(location_dir))


def save_pipeline_result(location_dir, pipeline_result):
    __save_to_file(pipeline_result, get_pipeline_result_path(location_dir),
                   file_type=FileType.PICKLE)


def load_pipeline_result(location_dir):
    return __load_from_file(get_pipeline_result_path(location_dir), file_type=FileType.PICKLE)


def delete_pipeline_result(location_dir): __delete_file(get_pipeline_result_path(location_dir))


def has_checkpoints_dir(location_dir): return has(get_checkpoints_dir_path(location_dir))


def make_checkpoints_dir(location_dir): make_dir(get_checkpoints_dir_path(location_dir))


def delete_checkpoints_dir(location_dir, need_confirm=True) -> bool:
    return delete_dir(get_checkpoints_dir_path(location_dir), need_confirm)


def save_checkpoint(location_dir, checkpoint, custom_path=None) -> str:
    loc_dir = Path(location_dir).resolve()
    if custom_path is not None:
        __save_to_file(checkpoint, custom_path, FileType.PICKLE)
        path = Path(custom_path).resolve()
        if path.is_relative_to(loc_dir):
            path = str(path.relative_to(loc_dir).as_posix())
        else:
            path = custom_path
    else:
        path = Path(__get_checkpoint_path(location_dir)).resolve()
        __save_to_file(checkpoint, path, FileType.PICKLE)
        path = str(path.relative_to(loc_dir).as_posix())
    return path


def load_checkpoint(cp_path): return __load_from_file(cp_path, FileType.PICKLE)


def delete_checkpoint(location_dir, cp_path):
    path = resolve_checkpoint_path(location_dir, cp_path)
    if path is None:
        raise NotExistsXManError(f"Can't resolve checkpoint path `{cp_path}`!")
    __delete_file(path)


def save_checkpoints_list(location_dir, cp_list):
    __save_to_file(cp_list, get_checkpoints_list_path(location_dir), FileType.JSON)


def load_checkpoints_list(location_dir) -> Optional[Any]:
    return __load_from_file(get_checkpoints_list_path(location_dir), FileType.JSON)


def delete_checkpoints_list(location_dir): __delete_file(get_checkpoints_list_path(location_dir))


def resolve_checkpoint_path(location_dir: str, cp_path: str) -> Optional[str]:
    cp_p = Path(cp_path)
    ld_p = Path(location_dir)
    path = ld_p / cp_p
    if path.resolve().exists():
        return str(path.as_posix())
    if cp_p.resolve().exists():
        return cp_path
    return None


def save_note(location_dir, obj, file_type: FileType):
    __save_to_file(obj, get_note_path(location_dir, file_type), file_type)


def load_note(location_dir, file_type: FileType):
    return __load_from_file(get_note_path(location_dir, file_type), file_type)


def delete_note(location_dir, file_type): __delete_file(get_note_path(location_dir, file_type))
