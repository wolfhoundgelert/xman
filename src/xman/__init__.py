__version__ = '0.0.10'  #TODO support auto setting from setup.py


from .api import ExpProjAPI


proj: ExpProjAPI = None


def dir_tree(target_dir, files_limit=10, files_first=True, sort_numbers=True):
    xman.dir_tree(target_dir, files_limit, files_first, sort_numbers)


def make_proj(location_dir: str, name: str, descr: str):
    return xman.make_proj(location_dir, name, descr)


def load_proj(location_dir: str): return xman.load_proj(location_dir)


def info(): xman.info()


def make_group(name, descr, num=None): return xman.make_group(name, descr, num)


def destroy_group(num_or_name, need_confirm=True):
    return xman.destroy_group(num_or_name, need_confirm)


def group(num_or_name): return xman.group(num_or_name)


def groups(): return xman.groups()


def make_exp(group_num_or_name, name, descr, num=None):
    return xman.make_exp(group_num_or_name, name, descr, num)


def destroy_exp(dot_num: str, need_confirm=True):
    return xman.destroy_exp(dot_num, need_confirm)


def exp(dot_num: str): return xman.exp(dot_num)


def exps(group_num_or_name=None): return xman.exps(group_num_or_name)


def start(exp_dot_num: str = None, autostart_next=False):
    return xman.start(exp_dot_num, autostart_next)


class xman:

    proj = None

    @staticmethod
    def dir_tree(target_dir, files_limit=10, files_first=True, sort_numbers=True):
        from . import tree
        tree.print_dir_tree(target_dir, files_limit, files_first, sort_numbers)

    @staticmethod
    def make_proj(location_dir: str, name: str, descr: str):
        from . import maker
        obj = maker._make_proj(location_dir, name, descr)
        return xman.__make_proj_api(obj)

    @staticmethod
    def load_proj(location_dir: str):
        from . import maker
        obj = maker._recreate_proj(location_dir)
        return xman.__make_proj_api(obj)

    @staticmethod
    def info():
        xman.__check_proj()
        xman.proj.info()

    @staticmethod
    def make_group(name, descr, num=None):
        xman.__check_proj()
        return xman.proj.make_group(name, descr, num)

    @staticmethod
    def destroy_group(num_or_name, need_confirm=True):
        xman.__check_proj()
        return xman.proj.destroy_group(num_or_name, need_confirm)

    @staticmethod
    def group(num_or_name):
        xman.__check_proj()
        return xman.proj.group(num_or_name)

    @staticmethod
    def groups():
        xman.__check_proj()
        return xman.proj.groups()

    @staticmethod
    def make_exp(group_num_or_name, name, descr, num=None):
        xman.__check_proj()
        return xman.proj.make_exp(group_num_or_name, name, descr, num)

    @staticmethod
    def destroy_exp(dot_num: str, need_confirm=True):
        xman.__check_proj()
        return xman.proj.destroy_exp(dot_num, need_confirm)

    @staticmethod
    def exp(dot_num: str):
        xman.__check_proj()
        return xman.proj.exp(dot_num)

    @staticmethod
    def exps(group_num_or_name=None):
        xman.__check_proj()
        return xman.proj.exps(group_num_or_name)

    @staticmethod
    def start(exp_dot_num: str = None, autostart_next=False):
        xman.__check_proj()
        xman.proj.start(exp_dot_num, autostart_next)

    @staticmethod
    def __make_proj_api(obj):
        from .api import ExpProjAPI
        xman.proj = ExpProjAPI(obj)
        global proj
        proj = xman.proj
        return xman.proj

    @staticmethod
    def __check_proj():
        from .error import IllegalOperationXManError
        if xman.proj is None:
            raise IllegalOperationXManError(f"There's no project - use `xman.make_proj(...)` or "
                                            f"`xman.load_proj(...)` first!")
