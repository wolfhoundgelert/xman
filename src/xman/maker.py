from typing import Optional

from .error import AlreadyExistsXManError, ArgumentsXManError, IllegalOperationXManError
from .exp import Exp, ExpData
from .group import ExpGroup
from .pipeline import PipelineData, PipelineRunData, Pipeline
from . import util, filesystem, platform
from .proj import ExpProj
from .struct import ExpStruct, ExpStructData


def __get_data_class(obj_cls):
    if obj_cls == Exp:
        return ExpData
    elif issubclass(obj_cls, ExpStruct):
        return ExpStructData
    else:
        raise ArgumentsXManError(f"`obj_cls` should inherit `ExpStruct`!")


def make_proj(location_dir, name, descr) -> ExpProj:
    make_and_save_struct_data(ExpProj, location_dir, name, descr)
    return ExpProj(location_dir)


def recreate_proj(location_dir) -> Optional[ExpProj]:
    proj = ExpProj(location_dir)
    if platform.is_colab:
        if not platform.check_colab_forked_folders(proj):
            return None
        for group in proj.groups():
            if not platform.check_colab_forked_folders(group):
                return None


def make_and_save_struct_data(struct_cls, location_dir, name, descr):
    filesystem.prepare_dir(location_dir) if struct_cls == ExpProj else \
        filesystem.make_dir(location_dir, exist_ok=False)
    data = __get_data_class(struct_cls)(name, descr)
    filesystem.save_data_and_time(data, location_dir)


def get_child_class(parent_obj_or_cls):
    cls = util.get_cls(parent_obj_or_cls)
    if cls == ExpProj:
        return ExpGroup
    elif cls == ExpGroup:
        return Exp
    else:
        raise ArgumentsXManError(f"`parent_obj_or_cls` should be `ExpProj` or `ExpGroup`!")


def make_new_child(parent, name, descr, child_num) -> Optional[Exp | ExpGroup]:
    child_class = get_child_class(parent)
    child_dir = filesystem.get_child_dir(parent, child_num)
    make_and_save_struct_data(child_class, child_dir, name, descr)
    child = child_class(child_dir, parent)
    if platform.is_colab:
        return child if platform.check_colab_forked_folders(parent) else None
    return child


def recreate_child(parent, child_num):
    location_dir = filesystem.get_child_dir(parent, child_num)
    return get_child_class(parent)(location_dir, parent)


def delete_child(child: Exp | ExpGroup, need_confirm) -> bool:
    if not filesystem.delete_dir(child.location_dir, need_confirm):
        return False
    child._destroy()
    return True


def make_pipeline(exp, run_func, with_mediator, params, save_on_storage=False):
    if exp._data.pipeline is not None:
        raise AlreadyExistsXManError(f"`{exp}` already has a pipeline!")
    exp._data.pipeline = PipelineData()
    run_data = PipelineRunData(run_func, with_mediator, params)
    if save_on_storage:
        filesystem.save_pipeline_run_data(run_data, exp.location_dir)
    return Pipeline(exp.location_dir, exp._data.pipeline, run_data)


def recreate_pipeline(exp):
    run_data = filesystem.load_pipeline_run_data(exp.location_dir)
    if run_data is None:
        raise IllegalOperationXManError(f"Can't recreate pipeline for exp `{exp}` - "
                                        f"there's no `.run` file! Use `save=True` for "
                                        f"`make_pipeline` method if you need to preserve "
                                        f"`run_func` and `params` for other session.")
    return Pipeline(exp.location_dir, exp._data.pipeline, run_data)


def delete_pipeline(exp: Exp, pipeline: Optional[Pipeline]):
    exp.delete_checkpoints(need_confirm=False, delete_custom_paths=True)
    filesystem.delete_pipeline_run_data(exp.location_dir)
    filesystem.delete_run_timestamp(exp.location_dir)
    if pipeline is not None:
        pipeline._destroy()
    exp._data.pipeline = None
