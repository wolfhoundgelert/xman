from .proj import ExpProj
from . import tree
from . import platform
from . import maker


__version__ = '0.0.8'  #TODO support auto setting from setup.py


proj: ExpProj = None


def dir_tree(target_dir, files_limit=10, files_first=True, sort_numbers=True):
    tree.print_dir_tree(target_dir, files_limit, files_first, sort_numbers)


def make_proj(location_dir: str, name: str, descr: str) -> ExpProj:
    maker._make_and_save_data(ExpProj, location_dir, name, descr)
    global proj
    proj = ExpProj(location_dir)
    return proj


def load_proj(location_dir: str) -> ExpProj:
    global proj
    proj = ExpProj(location_dir)
    if platform.is_colab:
        if not platform.check_colab_forked_folders(proj):
            return None
        for group in proj.groups():
            if not platform.check_colab_forked_folders(group):
                return None
    return proj


# TODO xman.exp(1.1) direct call without project
# TODO xman.group(1) direct call without project
# TODO xman.make_group()
# TODO xman.make_exp(group_num, name, descr)
# TODO xman.info() and so on
