import os
import re


def _create_dir(dir_path):
    if os.path.exists(dir_path):
        if not os.path.isdir(dir_path):
            raise NotADirectoryError(f"`{dir_path}` is not a directory!")
        elif len(os.listdir(dir_path)) > 0:
            raise AssertionError(f"Directory `{dir_path}` should be empty!")
    else:
        os.mkdir(dir_path)

    return dir_path


def _check_num(num, allow_none):
    if type(num) is int:
        if num >= 1:
            return
    else:
        if allow_none and num is None:
            return

    if allow_none:
        raise ValueError(f"num={num} should be None or an integer that greater than 0!")
    raise ValueError(f"num={num} should be an integer that greater than 0!")


def _get_dir_nums_by_pattern(location_dir, dir_pattern):
    regex = fr'{dir_pattern}([1-9][0-9]*)'
    names = os.listdir(location_dir)
    dirs = [x for x in names if os.path.isdir(os.path.join(location_dir, x))]
    nums = []

    for it in dirs:
        match = re.search(regex, it)

        if re.search(regex, it):
            nums.append(int(match.group(1)))

    return nums
