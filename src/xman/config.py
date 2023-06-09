from xman import util


class PipelineConfig:

    timer_interval = 2 * util.SECOND
    active_buffer = 5 * util.SECOND
    active_buffer_colab = util.MINUTE


confirm_off = False
is_pytest = False


def set__is_pytest(value):
    global is_pytest, confirm_off
    is_pytest = value
    confirm_off = is_pytest
