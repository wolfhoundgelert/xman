from typing import Optional

from .error import AlreadyExistsXManError, ArgumentsXManError, IllegalOperationXManError
from .pipeline import PipelineData, PipelineRunData, Pipeline
from . import util, filesystem, platform


def __get_data_class(obj_cls):
    from .exp import Exp, ExpData
    from .struct import ExpStructData, ExpStruct
    if obj_cls == Exp:
        return ExpData
    elif issubclass(obj_cls, ExpStruct):
        return ExpStructData
    else:
        raise ArgumentsXManError(f"`obj_cls` should inherit `ExpStruct`!")


def _make_proj(location_dir, name, descr) -> 'ExpProj':
    from .proj import ExpProj
    _make_and_save_struct_data(ExpProj, location_dir, name, descr)
    return ExpProj(location_dir)


def _recreate_proj(location_dir) -> Optional['ExpProj']:
    from .proj import ExpProj
    proj = ExpProj(location_dir)
    if platform.is_colab:
        if not platform.check_colab_forked_folders(proj):
            return None
        for group in proj.groups():
            if not platform.check_colab_forked_folders(group):
                return None


def _make_and_save_struct_data(struct_cls, location_dir, name, descr):
    from .proj import ExpProj
    filesystem._prepare_dir(location_dir) if struct_cls == ExpProj else \
        filesystem._make_dir(location_dir)
    data = __get_data_class(struct_cls)(name, descr)
    filesystem._save_data_and_time(data, location_dir)


def _get_child_class(parent_obj_or_cls):
    from .proj import ExpProj
    from .group import ExpGroup
    from .exp import Exp
    cls = util.get_cls(parent_obj_or_cls)
    if cls == ExpProj:
        return ExpGroup
    elif cls == ExpGroup:
        return Exp
    else:
        raise ArgumentsXManError(f"`parent_obj_or_cls` should be `ExpProj` or `ExpGroup`!")


def _make_new_child(parent, name, descr, child_num) -> Optional['ExpStruct']:
    child_class = _get_child_class(parent)
    child_dir = filesystem._get_child_dir(parent, child_num)
    _make_and_save_struct_data(child_class, child_dir, name, descr)
    child = child_class(child_dir, parent)
    if platform.is_colab:
        return child if platform.check_colab_forked_folders(parent) else None
    return child


def _recreate_child(parent, child_num):
    location_dir = filesystem._get_child_dir(parent, child_num)
    return _get_child_class(parent)(location_dir, parent)


def _destroy_child(child: 'ExpStruct'):
    child._destroy()
    filesystem._delete_dir(child._location_dir)


def _make_pipeline(exp, run_func, with_mediator, params, save=False):
    if exp._data.pipeline is not None:
        raise AlreadyExistsXManError(f"`{exp}` already has a pipeline!")
    exp._data.pipeline = PipelineData()
    run_data = PipelineRunData(run_func, with_mediator, params)
    if save:
        filesystem._save_pipeline_run_data(run_data, exp._location_dir)
    return Pipeline(exp._location_dir, exp._data.pipeline, run_data)


def _recreate_pipeline(exp):
    run_data = filesystem._load_pipeline_run_data(exp._location_dir)
    if run_data is None:
        raise IllegalOperationXManError(f"Can't recreate pipeline for exp `{exp}` - "
                                        f"there's no `.run` file! Use `save=True` for "
                                        f"`make_pipeline` method if you need to preserve "
                                        f"`run_func` and `params` for other session.")
    return Pipeline(exp._location_dir, exp._data.pipeline, run_data)


def _destroy_pipeline(exp, pipeline, keep_data: bool):
    filesystem._delete_pipeline_run_data(exp._location_dir)
    if pipeline is not None:
        pipeline._destroy()
    if not keep_data:
        exp._data.pipeline = None
