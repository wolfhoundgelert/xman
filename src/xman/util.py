from .error import OverrideXManError, ArgumentsXManError


SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR


TAB_NUM_SPACES = 4


def tab(text, deep=1):
    t = ' ' * TAB_NUM_SPACES * deep
    return text.replace('\n', f'\n{t}')


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


def get_cls(target_obj_or_cls):
    t = type(target_obj_or_cls)
    return target_obj_or_cls if t == type else t


def check_has_value_in_class_public_constants(value, instance_or_cls):
    cls = get_cls(instance_or_cls)
    constants = [v for it in vars(cls).items() if isinstance(v := it[1], str) and v.upper() == v
                 and not v.startswith(('_', '__'))]
    if value not in constants:
        raise ArgumentsXManError(f"Wrong value `{value}`, should be one of {constants}")


def override_it(): raise OverrideXManError("Should be overriden!")


def warning(message: str): print('\nWARNING! ' + message + '\n')
