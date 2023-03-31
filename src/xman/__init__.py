from .proj import ExpProj
from .tree import _print_dir_tree


def make_proj(location_dir: str, name: str, descr: str) -> ExpProj:
    return ExpProj._make(location_dir, name, descr)


def load_proj(location_dir: str) -> ExpProj:
    return ExpProj._load(location_dir)


def dir_tree(target_dir):
    _print_dir_tree(target_dir)
