import traceback


def get_error_str(error: Exception) -> str:
    return f"{error.__class__.__name__}: {error.args[0] if len(error.args) == 1 else error.args}"


def get_error_stack_str(error: Exception) -> str:
    stack = 'Traceback (most recent call last):\n'
    stack += ''.join(traceback.format_tb(error.__traceback__))
    stack += 'ERROR:\n    ' + get_error_str(error)
    return stack


class XManError(Exception):  # It's better not to use this generic error
    pass


class IllegalOperationXManError(XManError):
    pass


class NotExistsXManError(XManError):
    pass


class AlreadyExistsXManError(XManError):
    pass


class WasDestroyedXManError(XManError):
    pass


class ArgumentsXManError(XManError):
    pass


class OverrideXManError(XManError):
    pass


class NothingToDoXManError(XManError):
    pass


class NotImplementedXManError(XManError):
    pass


class PlatformXManError(XManError):
    pass
