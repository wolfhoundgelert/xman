import os
import re

from xman.error import OverrideXManError, ArgumentsXManError

SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR

__DOT_NUM_REGEX = r'^([1-9]\d*)\.([1-9]\d*)$'

TAB = '    '


def tab(text, num=1):
    t = TAB * num
    text = text.replace('\n', f'\n{t}')
    return f"{t}{text}"


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


def parse_group_and_exp_num(dot_num: str):
    match = re.match(__DOT_NUM_REGEX, dot_num)
    if match is None:
        raise ArgumentsXManError(f"`dot_num` should be a string like `1.1`, `2.3`, etc, but `{dot_num}` was given")
    group_num, exp_num = int(match[1]), int(match[2])
    return group_num, exp_num


def response(question):
    r = input(f"{question} (y/n) ")
    return r.lower() == "y"


def get_cls(target_obj_or_cls):
    t = type(target_obj_or_cls)
    return target_obj_or_cls if t == type else t


def override_it(): raise OverrideXManError("Should be overriden!")


def warning(message: str): print('\nWARNING! ' + message + '\n')
