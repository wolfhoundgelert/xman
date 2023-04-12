import os
import re


SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR


def make_dir(dir_path):
    if os.path.exists(dir_path):
        if not os.path.isdir(dir_path):
            raise NotADirectoryError(f"`{dir_path}` is not a directory!")
        elif len(os.listdir(dir_path)) > 0:
            raise AssertionError(f"Directory `{dir_path}` should be empty!")
    else:
        os.mkdir(dir_path)


def is_num(num_or_name):
    return type(num_or_name) is int and num_or_name >= 1


def is_name(num_or_name):
    return type(num_or_name) is str


def check_num(num, allow_none: bool):
    if is_num(num):
        return
    if allow_none:
        if num is None:
            return
        raise ValueError(f"num={num} should be None or an integer that greater or equal 1!")
    raise ValueError(f"num={num} should be an integer that greater or equal 1!")


def get_dir_num(target_dir):
    regex = fr'[1-9][0-9]*$'
    match = re.search(regex, target_dir)
    return int(match.group()) if match else None


def get_dir_nums_by_pattern(location_dir, dir_pattern):
    regex = fr'^{dir_pattern}([1-9][0-9]*)$'
    names = os.listdir(location_dir)
    dirs = [x for x in names if os.path.isdir(os.path.join(location_dir, x))]
    nums = []
    for it in dirs:
        match = re.search(regex, it)
        if match:
            nums.append(int(match.group(1)))
    nums.sort()
    return nums


def parse_group_and_exp_num(dot_num: float):
    nums = str(dot_num).split('.')
    if len(nums) != 2:
        raise ValueError(f"dot_num should be dotted float like 1.1, 2.3, etc, but `{dot_num}` was given")
    group_num, exp_num = int(nums[0]), int(nums[1])
    check_num(group_num, False)
    check_num(exp_num, False)
    return group_num, exp_num


def debug(message: str):
    print('DEBUG: ' + message)
