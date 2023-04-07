from .struct import ExpStructStatus


_AUTO_STATUS_RESOLUTION = '-= auto status =-'


# TODO make unit test
def _dict_has_status(structures_dict, status_or_list, all: bool):
    status = status_or_list if type(status_or_list) is str else None
    status_list = status_or_list if type(status_or_list) is list else None
    if status is None and status_list is None:
        raise ValueError(f"status_or_list = {status_or_list} should be string or list of strings!")
    for struct in structures_dict.values():
        s = struct.status()
        if status:
            if all:
                if s != status:
                    return False
            else:
                if s == status:
                    return True
        else:
            if all:
                if s not in status_list:
                    return False
            else:
                if s in status_list:
                    return True
    return True if all else False

# TODO implement ExpStructContainer and move it there
def _process_status(struct_container):
    if struct_container.data.manual_status is not None:
        status = struct_container.data.manual_status
        resolution = struct_container.data.manual_status_resolution
        manual = True
    else:
        resolution = _AUTO_STATUS_RESOLUTION
        manual = False
        dict = struct_container._num_to_child
        if _dict_has_status(dict, ExpStructStatus.ERROR, False):
            status = ExpStructStatus.ERROR
        elif _dict_has_status(dict, ExpStructStatus.IN_PROGRESS, False):
            status = ExpStructStatus.IN_PROGRESS
        elif _dict_has_status(dict, ExpStructStatus.EMPTY, True):
            status = ExpStructStatus.EMPTY
        elif _dict_has_status(dict, ExpStructStatus.TODO, True):
            status = ExpStructStatus.TODO
        elif _dict_has_status(dict, ExpStructStatus.DONE, True):
            status = ExpStructStatus.DONE
        elif _dict_has_status(dict, ExpStructStatus.SUCCESS, True):
            status = ExpStructStatus.SUCCESS
        elif _dict_has_status(dict, ExpStructStatus.FAIL, True):
            status = ExpStructStatus.FAIL
        elif _dict_has_status(
                dict, [ExpStructStatus.DONE, ExpStructStatus.SUCCESS, ExpStructStatus.FAIL], True):
            status = ExpStructStatus.DONE
        else:
            status = ExpStructStatus.IN_PROGRESS
    struct_container.status = ExpStructStatus(status, resolution, manual)
