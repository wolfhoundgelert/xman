import os
import re


def _make_dir(dir_path):
    if os.path.exists(dir_path):
        if not os.path.isdir(dir_path):
            raise NotADirectoryError(f"`{dir_path}` is not a directory!")
        elif len(os.listdir(dir_path)) > 0:
            raise AssertionError(f"Directory `{dir_path}` should be empty!")
    else:
        os.mkdir(dir_path)
    return dir_path


def _is_num(val):
    return type(val) is int and val >= 1


def _is_name(num_or_name):
    return type(num_or_name) is str


def _check_num(num, allow_none):
    if _is_num(num):
        return num
    if allow_none:
        if num is None:
            return num
        raise ValueError(f"num={num} should be None or an integer that greater or equal 1!")
    raise ValueError(f"num={num} should be an integer that greater or equal 1!")


def _get_dir_num(target_dir):
    regex = fr'[1-9][0-9]*$'
    match = re.search(regex, target_dir)
    return int(match.group()) if match else None


def _get_dir_nums_by_pattern(location_dir, dir_pattern):
    regex = fr'{dir_pattern}([1-9][0-9]*)$'
    names = os.listdir(location_dir)
    dirs = [x for x in names if os.path.isdir(os.path.join(location_dir, x))]
    nums = []
    for it in dirs:
        match = re.search(regex, it)
        if match:
            nums.append(int(match.group(1)))
    return nums


def _has_in_num_or_name_dicts(num_or_name, num_dict, name_dict):
    if _is_num(num_or_name):
        return num_or_name in num_dict
    elif _is_name(num_or_name):
        return num_or_name in name_dict
    else:
        raise ValueError(f"`num_or_name` should be num >= 1 (int) or name (str), but {num_or_name} was given!")


def _get_by_num_or_name(num_or_name, num_dict, name_dict):
    if _is_num(num_or_name) and num_or_name in num_dict:
        return num_dict[num_or_name]
    elif _is_name(num_or_name) and num_or_name in name_dict:
        return name_dict[num_or_name]
    raise ValueError(f"There's no item with num or name `{num_or_name}`!")


def _get_highest_num_in_dict(target: dict):
    l = target.keys()
    return max(l) if len(l) else 0


def _parse_group_and_exp_num(dot_num: float):
    nums = str(dot_num).split('.')
    if len(nums) != 2:
        raise ValueError(f"dot_num should be dotted float like 1.1, 2.3, etc, but `{dot_num}` was given")
    group_num, exp_num = int(nums[0]), int(nums[1])
    _check_num(group_num, False)
    _check_num(exp_num, False)
    return group_num, exp_num
