import os
import sys

from xman import config


def test__xman_init():  # Just for adding xman's `src` to paths and config `is_pytest` setting
    xman_path = os.path.abspath(os.path.join('src'))
    if xman_path not in sys.path:
        sys.path.insert(0, xman_path)
    config.set__is_pytest(True)


from xman import xman
import helper


def test__config():
    config.is_pytest = True


def test__make_proj():
    proj = helper.make_proj_from_nothing()
    assert proj.name == 'Test Proj' and xman.proj.descr == 'Test proj descr'


def test__pipeline():
    exp = helper.make_exp_from_nothing().make_pipeline(helper.train, helper.train_params, True).\
        start()
    assert exp.result == helper.train_result


def test__destroy_group():
    helper.make_exp_from_nothing()
    xman.proj.destroy_group(1)
    assert xman.proj.num_children == 0


def test__destroy_exp():
    helper.make_exp_from_nothing()
    xman.proj.group(1).destroy_exp(1)
    assert xman.proj.group(1).num_children == 0

def test__destroy_exp_after_pipeline_done():
    helper.make_exp_from_nothing().make_pipeline(helper.train, helper.train_params, True).start()
    xman.proj.group(1).destroy_exp(1)
