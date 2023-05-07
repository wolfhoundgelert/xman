confirm_off = False
is_pytest = False


def set__is_pytest(value):
    global is_pytest, confirm_off
    is_pytest = value
    confirm_off = is_pytest