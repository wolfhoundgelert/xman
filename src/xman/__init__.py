from . import proj


def create_project(location_dir: str, name: str, descr: str):
    return proj.ExperimentalProject._create(location_dir, name, descr)


def load_project(location_dir: str):
    return proj.ExperimentalProject._load(location_dir)
