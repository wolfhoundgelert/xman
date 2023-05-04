from .error import AlreadyExistsXManError, ArgumentsXManError, IllegalOperationXManError
from .pipeline import PipelineData, PipelineRunData, Pipeline
from . import util
from . import filesystem
from . import platform


def __get_data_class(obj_cls):
    from .exp import Exp, ExpData
    from .struct import ExpStructData, ExpStruct

    if obj_cls == Exp:
        return ExpData
    elif issubclass(obj_cls, ExpStruct):
        return ExpStructData
    else:
        raise ArgumentsXManError(f"`obj_cls` should inherit `ExpStruct`!")


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


def _destroy_child(child, confirm):
    return filesystem._delete_struct(child, confirm)


def _make_pipeline(exp, run_func, params, save=False):
    if exp._data.pipeline is not None:
        raise AlreadyExistsXManError(f"Exp `{exp}` already has a pipeline!")
    exp._data.pipeline = PipelineData(False, False, None, None, None, None)
    run_data = PipelineRunData(run_func, params)
    if save:
        filesystem._save_pipeline_run_data(run_data, exp.location_dir)
    return Pipeline(exp.location_dir, exp._data.pipeline, run_data)


def _recreate_pipeline(exp):
    run_data = filesystem._load_pipeline_run_data(exp.location_dir)
    if run_data is None:
        raise IllegalOperationXManError(f"Can't recreate pipeline for exp `{exp}` - there's no `.run` file! "
            f"Use `save=True` for `make_pipeline` method if you need to preserve `run_func` and `params` "
            f"for other session.")
    return Pipeline(exp.location_dir, exp._data.pipeline, run_data)


def _destroy_pipeline(exp, pipeline, keep_data: bool):
    filesystem._delete_pipeline_run_data(exp.location_dir)
    if pipeline is not None:
        pipeline._destroy()
    if not keep_data:
        exp._data.pipeline = None

