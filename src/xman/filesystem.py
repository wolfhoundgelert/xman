import os
import shutil
import time
import re
from typing import Optional, Any
from datetime import datetime

import cloudpickle as pickle  # dill as pickle, pickle

from .error import ArgumentsXManError, IllegalOperationXManError, NotImplementedXManError
from . import util
from . import maker


def __get_data_path(location_dir): return os.path.join(location_dir, '.data')


def __get_time_path(location_dir): return os.path.join(location_dir, '.time')


def __get_run_path(location_dir): return os.path.join(location_dir, '.run')


def __get_run_time_path(location_dir): return os.path.join(location_dir, '.run_time')


def _get_checkpoints_dir_path(location_dir): return os.path.join(location_dir, 'checkpoints/')


def __get_checkpoints_list_path(location_dir):
    return os.path.join(_get_checkpoints_dir_path(location_dir), '.list')


def __get_checkpoint_path(location_dir):
    fname = str(datetime.utcnow()).replace(' ', '__').replace(':', '_').replace('.', '--') + '.cp'
    return os.path.join(_get_checkpoints_dir_path(location_dir), fname)


def _get_dir_num(target_dir):
    match = re.search(fr'[1-9][0-9]*$', target_dir)
    return int(match.group()) if match else None


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


def _dir_prefix(struct_obj_or_cls):
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


def _get_child_dir(parent, child_num):
    return os.path.join(parent._location_dir, _dir_prefix(maker._get_child_class(parent)) +
                        str(child_num))


def _get_children_nums(parent):
    child_class = maker._get_child_class(parent)
    child_dir_prefix = _dir_prefix(child_class)
    return __get_dir_nums_by_pattern(parent._location_dir, child_dir_prefix)


def _has(path) -> bool: return os.path.exists(path)


def _make_dir(dir_path):
    if _has(dir_path):
        raise ArgumentsXManError(f"Dir path `{dir_path}` already exists!")
    else:
        os.makedirs(dir_path, exist_ok=True)


def _prepare_dir(dir_path):
    if _has(dir_path):
        if not os.path.isdir(dir_path):
            raise ArgumentsXManError(f"`{dir_path}` is not a directory!")
        elif len(os.listdir(dir_path)) > 0:
            raise IllegalOperationXManError(f"Directory `{dir_path}` should be empty!")
    else:
        os.mkdir(dir_path)


def __save(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        pickle.dump(obj, f)


def __load(path):
    with open(path, 'rb') as f:
        return pickle.load(f)


def _save_data_and_time(data, location_dir) -> float:
    __save(data, __get_data_path(location_dir))
    t = time.time()
    __save(t, __get_time_path(location_dir))
    return t


def _load_fresh_data_and_time(location_dir, last_data, last_time):
    t = __load(__get_time_path(location_dir))
    if last_time != t:
        return __load(__get_data_path(location_dir)), t
    return last_data, last_time


def _delete_dir(dir_path) -> bool:
    if _has(dir_path):
        shutil.rmtree(dir_path, ignore_errors=True)
        return True
    return False


def _delete_file(file_path) -> bool:
    if _has(file_path):
        os.remove(file_path)
        return True
    return False


def _load_from_file(file_path) -> Optional[Any]:
    if _has(file_path):
        return __load(file_path)
    return None


def _save_pipeline_run_data(run_data, location_dir):
    __save(run_data, __get_run_path(location_dir))


def _load_pipeline_run_data(location_dir): return _load_from_file(__get_run_path(location_dir))


def _delete_pipeline_run_data(location_dir): _delete_file(__get_run_path(location_dir))


def _save_run_time(location_dir): __save(time.time(), __get_run_time_path(location_dir))


def _load_run_time(location_dir): return _load_from_file(__get_run_time_path(location_dir))


def _delete_run_time(location_dir): _delete_file(__get_run_time_path(location_dir))


def _has_checkpoints_dir(location_dir): return _has(_get_checkpoints_dir_path(location_dir))


def _make_checkpoints_dir(location_dir):
    p = _get_checkpoints_dir_path(location_dir)
    if not _has(p):
        _make_dir(p)


def _delete_checkpoints_dir(location_dir): _delete_dir(_get_checkpoints_dir_path(location_dir))


def _save_checkpoint(checkpoint, location_dir, custom_path=None) -> str:
    p = __get_checkpoint_path(location_dir) if custom_path is None else custom_path
    __save(checkpoint, p)
    return p


def _load_checkpoint(cp_path): return _load_from_file(cp_path)


def _delete_checkpoint(cp_path): _delete_file(cp_path)


def _save_checkpoints_list(cp_list, location_dir):
    __save(cp_list, __get_checkpoints_list_path(location_dir))


def _load_checkpoints_list(location_dir):
    return _load_from_file(__get_checkpoints_list_path(location_dir))


def _delete_checkpoints_list(location_dir): _delete_file(__get_checkpoints_list_path(location_dir))
