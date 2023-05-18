from . import config
from .struct import ExpStruct


def __response(question):
    r = input(f"{question} (y/n) ")
    return r.lower() == "y"


def request(need_confirm, request):
    if config.confirm_off:
        return True
    return __response(request) if need_confirm else True


def delete_struct_and_all_its_content(struct: ExpStruct, need_confirm):
    p = struct.location_dir
    return request(need_confirm,
                    f"ATTENTION! Remove `{struct}` and all its `{p}` dir with all its content?")
