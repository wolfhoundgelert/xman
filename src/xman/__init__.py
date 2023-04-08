from .proj import ExpProj
from .tree import _print_dir_tree


__version__ = '0.0.0'  #TODO support auto setting from setup.py


proj: ExpProj = None


def dir_tree(target_dir):
    _print_dir_tree(target_dir)


def make_proj(location_dir: str, name: str, descr: str) -> ExpProj:
    global proj
    proj = ExpProj(location_dir, name, descr)
    return proj


def load_proj(location_dir: str) -> ExpProj:
    global proj
    proj = ExpProj(location_dir, None, None)
    return proj


# TODO xman.exp(1.1) direct call without project
# TODO xman.group(1) direct call without project
# TODO xman.make_group()
# TODO xman.make_exp(group_num, name, descr)
# TODO xman.info() and so on
