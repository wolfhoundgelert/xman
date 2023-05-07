import os
import shutil
import time
import re
import cloudpickle as pickle  # dill as pickle, pickle

from .error import ArgumentsXManError, IllegalOperationXManError, NotImplementedXManError
from . import util
from . import maker


def __get_data_path(location_dir): return os.path.join(location_dir, '.data')


def __get_time_path(location_dir): return os.path.join(location_dir, '.time')


def __get_run_path(location_dir): return os.path.join(location_dir, '.run')


def __get_checkpoint_path(location_dir): return os.path.join(location_dir, '.checkpoint')


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
    return os.path.join(parent.location_dir,
                        _dir_prefix(maker._get_child_class(parent)) + str(child_num))


def _get_children_nums(parent):
    child_class = maker._get_child_class(parent)
    child_dir_prefix = _dir_prefix(child_class)
    return __get_dir_nums_by_pattern(parent.location_dir, child_dir_prefix)


def _make_dir(dir_path):
    if os.path.exists(dir_path):
        ArgumentsXManError(f"Dir path `{dir_path}` already exists!")
    else:
        os.mkdir(dir_path)


def _prepare_dir(dir_path):
    if os.path.exists(dir_path):
        if not os.path.isdir(dir_path):
            raise ArgumentsXManError(f"`{dir_path}` is not a directory!")
        elif len(os.listdir(dir_path)) > 0:
            raise IllegalOperationXManError(f"Directory `{dir_path}` should be empty!")
    else:
        os.mkdir(dir_path)


def __save(obj, path):
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


def _delete_dir(location_dir): shutil.rmtree(location_dir, ignore_errors=True)


def _save_pipeline_run_data(run_data, location_dir):
    __save(run_data, __get_run_path(location_dir))


def _load_pipeline_run_data(location_dir):
    p = __get_run_path(location_dir)
    if os.path.exists(p):
        return __load(p)
    return None


def _delete_pipeline_run_data(location_dir):
    p = __get_run_path(location_dir)
    if os.path.exists(p):
        os.remove(p)


def _save_checkpoint(checkpoint, location_dir):
    __save(checkpoint, __get_checkpoint_path(location_dir))


def _load_checkpoint(location_dir):
    p = __get_checkpoint_path(location_dir)
    if os.path.exists(p):
        return __load(p)
    return None


def _delete_checkpoint(location_dir):
    p = __get_checkpoint_path(location_dir)
    if os.path.exists(p):
        os.remove(p)
