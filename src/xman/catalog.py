import os
import time
import re
from pathlib import Path
from typing import Optional, Any

from .error import ArgumentsXManError, IllegalOperationXManError, NotImplementedXManError, \
    NotExistsXManError
from . import util, maker
from .filesystem import FileType
from . import filesystem as fs


# TODO `load` rename to `get`


def __get_struct_data_path(location_dir): return os.path.join(location_dir, '.data')


def __get_manual_result_path(location_dir): return os.path.join(location_dir, '.manual_result')


def __get_pipeline_run_path(location_dir): return os.path.join(location_dir, '.run')


def __get_pipeline_run_time_path(location_dir): return os.path.join(location_dir, '.run_time')


def __get_pipeline_result_path(location_dir): return os.path.join(location_dir, '.pipeline_result')


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


def has(path: str) -> bool: return fs.exists(path)


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


def prepare_dir(dir_path):
    if has(dir_path):
        if not os.path.isdir(dir_path):
            raise ArgumentsXManError(f"`{dir_path}` is not a directory!")
        elif len(os.listdir(dir_path)) > 0:
            raise IllegalOperationXManError(f"Directory `{dir_path}` should be empty!")
    else:
        fs.make_dir(dir_path)


def save_struct_data(location_dir, data):
    fs.save(__get_struct_data_path(location_dir), FileType.PICKLE, data)  # TODO FileType.JSON


def get_struct_data(location_dir):
    return fs.load(__get_struct_data_path(location_dir), FileType.PICKLE)  # TODO json


def has_manual_result(location_dir): return has(__get_manual_result_path(location_dir))


def save_manual_result(location_dir, manual_result):
    fs.save(__get_manual_result_path(location_dir), FileType.PICKLE, manual_result)


def load_manual_result(location_dir):
    return fs.load(__get_manual_result_path(location_dir), FileType.PICKLE)


def delete_manual_result(location_dir): fs.delete(__get_manual_result_path(location_dir))


def save_pipeline_run_data(location_dir, run_data):
    fs.save(__get_pipeline_run_path(location_dir), FileType.PICKLE, run_data)


def load_pipeline_run_data(location_dir):
    return fs.load(__get_pipeline_run_path(location_dir), FileType.PICKLE)


def delete_pipeline_run_data(location_dir): fs.delete(__get_pipeline_run_path(location_dir))


def save_pipeline_run_time(location_dir):
    # No need to save time into the file, because `os.path.getmtime(file_path)` will be used:
    fs.save(__get_pipeline_run_time_path(location_dir), FileType.PICKLE, '')


def load_pipeline_run_time(location_dir) -> Optional[float]:
    path = __get_pipeline_run_time_path(location_dir)
    return fs.get_mtime(path) if has(path) else None


def delete_pipeline_run_time(location_dir): fs.delete(__get_pipeline_run_time_path(location_dir))


def has_pipeline_result(location_dir): return has(__get_pipeline_result_path(location_dir))


def save_pipeline_result(location_dir, pipeline_result):
    fs.save(__get_pipeline_result_path(location_dir), FileType.PICKLE, pipeline_result)


def load_pipeline_result(location_dir):
    return fs.load(__get_pipeline_result_path(location_dir), FileType.PICKLE)


def delete_pipeline_result(location_dir): fs.delete(__get_pipeline_result_path(location_dir))


def has_checkpoints_dir(location_dir): return has(get_checkpoints_dir_path(location_dir))


def make_checkpoints_dir(location_dir): fs.make_dir(get_checkpoints_dir_path(location_dir))


def delete_checkpoints_dir(location_dir, need_confirm=True) -> bool:
    return fs.delete_dir(get_checkpoints_dir_path(location_dir), need_confirm)


def save_checkpoint(location_dir, checkpoint, custom_path=None) -> str:
    loc_dir = Path(location_dir).resolve()
    if custom_path is not None:
        fs.save(custom_path, FileType.PICKLE, checkpoint)
        path = Path(custom_path).resolve()
        if path.is_relative_to(loc_dir):
            path = str(path.relative_to(loc_dir).as_posix())
        else:
            path = custom_path
    else:
        path = Path(__get_checkpoint_path(location_dir)).resolve()
        fs.save(str(path), FileType.PICKLE, checkpoint)
        path = str(path.relative_to(loc_dir).as_posix())
    return path


def load_checkpoint(cp_path): return fs.load(cp_path, FileType.PICKLE)


def delete_checkpoint(location_dir, cp_path):
    path = resolve_checkpoint_path(location_dir, cp_path)
    if path is None:
        raise NotExistsXManError(f"Can't resolve checkpoint path `{cp_path}`!")
    fs.delete(path)


def save_checkpoints_list(location_dir, cp_list):
    fs.save(get_checkpoints_list_path(location_dir), FileType.JSON, cp_list)


def load_checkpoints_list(location_dir) -> Optional[Any]:
    return fs.load(get_checkpoints_list_path(location_dir), FileType.JSON)


def delete_checkpoints_list(location_dir): fs.delete(get_checkpoints_list_path(location_dir))


def resolve_checkpoint_path(location_dir: str, cp_path: str) -> Optional[str]:
    cp_p = Path(cp_path)
    ld_p = Path(location_dir)
    path = ld_p / cp_p
    if path.resolve().exists():
        return str(path.as_posix())
    if cp_p.resolve().exists():
        return cp_path
    return None


def save_note(location_dir, note, file_type: FileType):
    fs.save(get_note_path(location_dir, file_type), file_type, note)


def load_note(location_dir, file_type: FileType):
    return fs.load(get_note_path(location_dir, file_type), file_type)


def delete_note(location_dir, file_type): fs.delete(get_note_path(location_dir, file_type))
