confirm_off = False
is_pytest = False


def set__is_pytest(value):
    global is_pytest
    is_pytest = value
    global confirm_off
    confirm_off = is_pytest