import os
import shutil
import time
import re
from typing import Optional, Any
from datetime import datetime

import cloudpickle as pickle  # dill as pickle, pickle

from .error import ArgumentsXManError, IllegalOperationXManError, NotImplementedXManError
from . import util, maker, confirm


def make_dir(dir_path, exist_ok=True): os.makedirs(dir_path, exist_ok=exist_ok)


def delete_dir(dir_path, need_confirm=True) -> bool:
    if len(os.listdir(dir_path)) > 0 and not confirm.request(
            need_confirm, f"ATTENTION! Dir `{dir_path}` isn't empty - delete anyway?"):
        return False
    shutil.rmtree(dir_path, ignore_errors=True)
    return True


def rename_or_move_dir(dir_path, new_path): shutil.move(dir_path, new_path)


def __get_data_path(location_dir): return os.path.join(location_dir, '.data')


def __get_time_path(location_dir): return os.path.join(location_dir, '.time')


def __get_run_path(location_dir): return os.path.join(location_dir, '.run')


def __get_run_time_path(location_dir): return os.path.join(location_dir, '.run_time')


def get_checkpoints_dir_path(location_dir): return os.path.join(location_dir, 'checkpoints/')


def __get_checkpoints_list_path(location_dir):
    return os.path.join(get_checkpoints_dir_path(location_dir), '.list')


def __get_checkpoint_path(location_dir):
    fname = str(datetime.utcnow()).replace(' ', '__').replace(':', '_').replace('.', '--') + '.cp'
    return os.path.join(get_checkpoints_dir_path(location_dir), fname)


def get_dir_num(target_dir):
    match = re.search(r'[1-9][0-9]*$', target_dir)
    return int(match.group()) if match else None


def change_num_in_path_by_pattern(path, pattern, new_num) -> str:
    return re.sub(fr'\b{pattern}[1-9][0-9]*\b', f'{pattern}{new_num}', path)


def change_exp_num_in_path(path: str, new_exp_num: int) -> str:
    return change_num_in_path_by_pattern(path, 'exp', new_exp_num)


def change_group_num_in_path(path: str, new_group_num: int) -> str:
    return change_num_in_path_by_pattern(path, 'group', new_group_num)


def __get_dir_nums_by_pattern(location_dir, dir_pattern):
    regex = fr'^{dir_pattern}([1-9][0-9]*)$'
    names = os.listdir(location_dir)
    dirs = [x for x in names if os.path.isdir(os.path.join(location_dir, x))]
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
            f"`struct_obj_or_cls` should be an instance of/or a final class inheriting ExpStruct!")


def get_child_dir(parent, child_num):
    return os.path.join(parent.location_dir, dir_prefix(maker.get_child_class(parent)) +
                        str(child_num))


def get_children_nums(parent):
    child_class = maker.get_child_class(parent)
    child_dir_prefix = dir_prefix(child_class)
    return __get_dir_nums_by_pattern(parent.location_dir, child_dir_prefix)


def __has(path) -> bool: return os.path.exists(path)


def prepare_dir(dir_path):
    if __has(dir_path):
        if not os.path.isdir(dir_path):
            raise ArgumentsXManError(f"`{dir_path}` is not a directory!")
        elif len(os.listdir(dir_path)) > 0:
            raise IllegalOperationXManError(f"Directory `{dir_path}` should be empty!")
    else:
        make_dir(dir_path)


def __save(obj, path):
    make_dir(os.path.dirname(path))
    with open(path, 'wb') as f:
        pickle.dump(obj, f)


def __load(path):
    with open(path, 'rb') as f:
        return pickle.load(f)


def save_data_and_time(data, location_dir) -> float:
    __save(data, __get_data_path(location_dir))
    t = time.time()
    __save(t, __get_time_path(location_dir))
    return t


def load_fresh_data_and_time(location_dir, last_data, last_time):
    t = __load(__get_time_path(location_dir))
    if last_time != t:
        return __load(__get_data_path(location_dir)), t
    return last_data, last_time


def __delete_file(file_path):
    if __has(file_path):
        os.remove(file_path)


def __load_from_file(file_path) -> Optional[Any]:
    if __has(file_path):
        return __load(file_path)
    return None


def save_pipeline_run_data(run_data, location_dir):
    __save(run_data, __get_run_path(location_dir))


def load_pipeline_run_data(location_dir): return __load_from_file(__get_run_path(location_dir))


def delete_pipeline_run_data(location_dir): __delete_file(__get_run_path(location_dir))


def save_run_time(location_dir): __save(time.time(), __get_run_time_path(location_dir))


def load_run_time(location_dir): return __load_from_file(__get_run_time_path(location_dir))


def delete_run_time(location_dir): __delete_file(__get_run_time_path(location_dir))


def has_checkpoints_dir(location_dir): return __has(get_checkpoints_dir_path(location_dir))


def make_checkpoints_dir(location_dir): make_dir(get_checkpoints_dir_path(location_dir))


def delete_checkpoints_dir(location_dir, need_confirm=True) -> bool:
    return delete_dir(get_checkpoints_dir_path(location_dir), need_confirm)


def save_checkpoint(checkpoint, location_dir, custom_path=None) -> str:
    p = __get_checkpoint_path(location_dir) if custom_path is None else custom_path
    __save(checkpoint, p)
    return p


def load_checkpoint(cp_path): return __load_from_file(cp_path)


def delete_checkpoint(cp_path): __delete_file(cp_path)


def save_checkpoints_list(cp_list, location_dir):
    __save(cp_list, __get_checkpoints_list_path(location_dir))


def load_checkpoints_list(location_dir):
    return __load_from_file(__get_checkpoints_list_path(location_dir))


def delete_checkpoints_list(location_dir): __delete_file(__get_checkpoints_list_path(location_dir))
