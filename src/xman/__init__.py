__version__ = '0.0.11'  # TODO support auto setting from setup.py


from . import tree, maker
from .api import ExpProjAPI
from .error import IllegalOperationXManError


class XMan:

    @staticmethod
    def dir_tree(target_dir, files_limit=10, files_first=True, sort_numbers=True):
        tree.print_dir_tree(target_dir, files_limit, files_first, sort_numbers)

    __proj: ExpProjAPI = None

    @property
    def proj(self) -> ExpProjAPI:
        self.__check_proj()
        self.__proj._update()
        return self.__proj

    def make_proj(self, location_dir: str, name: str, descr: str):
        obj = maker._make_proj(location_dir, name, descr)
        return self.__make_proj_api(obj)

    def load_proj(self, location_dir: str):
        obj = maker._recreate_proj(location_dir)
        return self.__make_proj_api(obj)

    def info(self):
        self.__check_proj()
        self.__proj.info()

    def make_group(self, name, descr, num=None):
        self.__check_proj()
        return self.__proj.make_group(name, descr, num)

    def destroy_group(self, num_or_name, need_confirm=True):
        self.__check_proj()
        return self.__proj.destroy_group(num_or_name, need_confirm)

    def group(self, num_or_name):
        self.__check_proj()
        return self.__proj.group(num_or_name)

    def groups(self):
        self.__check_proj()
        return self.__proj.groups()

    def make_exp(self, group_num_or_name, name, descr, num=None):
        self.__check_proj()
        return self.__proj.make_exp(group_num_or_name, name, descr, num)

    def destroy_exp(self, dot_num: str, need_confirm=True):
        self.__check_proj()
        return self.__proj.destroy_exp(dot_num, need_confirm)

    def exp(self, dot_num: str):
        self.__check_proj()
        return self.__proj.exp(dot_num)

    def exps(self, group_num_or_name=None):
        self.__check_proj()
        return self.__proj.exps(group_num_or_name)

    def start(self, exp_dot_num: str = None, autostart_next=False):
        self.__check_proj()
        self.__proj.start(exp_dot_num, autostart_next)

    def __make_proj_api(self, obj):
        if self.__proj is not None:
            self.__proj._destroy()
        self.__proj = ExpProjAPI(obj)
        return self.__proj

    def __check_proj(self):
        if self.__proj is None:
            raise IllegalOperationXManError(f"There's no project - use `xman.make_proj(...)` or "
                                            f"`xman.load_proj(...)` first!")


xman = XMan()
