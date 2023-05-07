from . import config


def __response(question):
    r = input(f"{question} (y/n) ")
    return r.lower() == "y"


def _request(need_confirm, request):
    if config.confirm_off:
        return True
    return __response(request) if need_confirm else True


def _remove_struct_and_all_its_content(struct: 'ExpStruct'):
    p = struct.location_dir
    return _request(True,
                    f"ATTENTION! Remove `{struct}` and all its `{p}` dir with all its content?")
