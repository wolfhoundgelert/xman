import shutil

from . import util, filesystem, platform
from .error import AlreadyExistsXManError, ArgumentsXManError
from .exp import Exp, ExpData
from .struct import ExpStruct, ExpStructData


def __get_data_class(obj_cls):
    if obj_cls == Exp:
        return ExpData
    elif issubclass(obj_cls, ExpStruct):
        return ExpStructData
    else:
        raise ArgumentsXManError(f"`obj_cls` should inherit `ExpStruct`!")


def _get_child_class(parent_obj_or_cls):
    from .group import ExpGroup
    from .proj import ExpProj

    cls = util.get_cls(parent_obj_or_cls)
    if cls == ExpProj:
        return ExpGroup
    elif cls == ExpGroup:
        return Exp
    else:
        raise ArgumentsXManError(f"`parent_obj_or_cls` should be `ExpProj` or `ExpGroup`!")


def _make_and_save_data(obj_cls, location_dir, name, descr):
    from .proj import ExpProj

    filesystem._prepare_dir(location_dir) if obj_cls == ExpProj else filesystem._make_dir(location_dir)
    data = __get_data_class(obj_cls)(name, descr)
    filesystem._save_data_and_time(data, location_dir)


def _make_new_child(parent, name, descr, child_num=None):
    util.check_num(child_num, True)
    if parent._has_child_num_or_name(name):
        raise AlreadyExistsXManError(f"A child with the name `{name}` already exists in the `{parent}`!")
    if child_num is not None:
        if parent._has_child_num_or_name(child_num):
            raise AlreadyExistsXManError(f"A child with the num `{child_num}` already exists in the `{parent}`!")
    else:
        nums = filesystem._get_children_nums(parent)
        max_num = max(nums) if len(nums) else 0
        child_num = max_num + 1
    child_class = _get_child_class(parent)
    child_dir = filesystem._get_child_dir(parent, child_num)
    _make_and_save_data(child_class, child_dir, name, descr)
    child = child_class(child_dir)
    if platform.is_colab:
        return child if platform.check_colab_forked_folders(parent) else None
    return child


def _recreate_child(parent, child_num):
    location_dir = filesystem._get_child_dir(parent, child_num)
    return _get_child_class(parent)(location_dir)
