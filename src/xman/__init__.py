from .proj import ExpProj
from .tree import print_dir_tree
from . import platform


__version__ = '0.0.0'  #TODO support auto setting from setup.py


proj: ExpProj = None


def dir_tree(target_dir, files_limit=10, files_first=True, sort_numbers=True):
    print_dir_tree(target_dir, files_limit, files_first, sort_numbers)


def make_proj(location_dir: str, name: str, descr: str) -> ExpProj:
    global proj
    proj = ExpProj(location_dir, name, descr)
    return proj


def load_proj(location_dir: str) -> ExpProj:
    global proj
    proj = ExpProj(location_dir, None, None)
    return proj if platform.check_forked_folders(proj) else None


# TODO xman.exp(1.1) direct call without project
# TODO xman.group(1) direct call without project
# TODO xman.make_group()
# TODO xman.make_exp(group_num, name, descr)
# TODO xman.info() and so on
