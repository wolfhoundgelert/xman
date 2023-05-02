import os
import re
import cloudpickle as pickle  # dill as pickle, pickle

from xman.error import OverrideXManError, ArgumentsXManError, IllegalOperationXManError

SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR

DOT_NUM_REGEX = r'^([1-9]\d*)\.([1-9]\d*)$'

TAB = '    '


def tab(text, num=1):
    tab = TAB * num
    text = text.replace('\n', f'\n{tab}')
    return f"{tab}{text}"


def make_dir(dir_path):
    if os.path.exists(dir_path):
        if not os.path.isdir(dir_path):
            raise ArgumentsXManError(f"`{dir_path}` is not a directory!")
        elif len(os.listdir(dir_path)) > 0:
            raise IllegalOperationXManError(f"Directory `{dir_path}` should be empty!")
    else:
        os.mkdir(dir_path)


def save(obj, location_dir, fname):
    fp = os.path.join(location_dir, fname)
    with open(fp, 'wb') as f:
        pickle.dump(obj, f)


def load(location_dir, fname):
    fp = os.path.join(location_dir, fname)
    with open(fp, 'rb') as f:
        return pickle.load(f)


def check_has_value_in_class_public_constants(value, instance_or_cls):
    t = type(instance_or_cls)
    # Check is this a class or an instance of some class (we need to take class)
    cls = instance_or_cls if t == type else t
    constants = [v for it in vars(cls).items() if isinstance(v := it[1], str) and v.upper() == v
                 and not v.startswith(('_', '__'))]
    if value not in constants:
        raise ArgumentsXManError(f"Wrong value `{value}`, should be one of `{constants}`")


def is_num(num_or_name): return type(num_or_name) is int and num_or_name >= 1


def is_name(num_or_name): return type(num_or_name) is str


def check_num(num, allow_none: bool):
    if is_num(num):
        return
    if allow_none:
        if num is None:
            return
        raise ArgumentsXManError(f"num={num} should be None or an integer that greater or equal 1!")
    raise ArgumentsXManError(f"num={num} should be an integer that greater or equal 1!")


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


def parse_group_and_exp_num(dot_num: str):
    match = re.match(DOT_NUM_REGEX, dot_num)
    if match is None:
        raise ArgumentsXManError(f"`dot_num` should be a string like `1.1`, `2.3`, etc, but `{dot_num}` was given")
    group_num, exp_num = int(match[1]), int(match[2])
    return group_num, exp_num


def response(question):
    r = input(f"{question} (y/n) ")
    return r.lower() == "y"


def override_it(): raise OverrideXManError("Should be overriden!")


def warning(message: str): print('\nWARNING! ' + message + '\n')
