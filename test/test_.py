import os
import sys
import pytest

from xman.error import IllegalOperationXManError


def test__xman_init():  # Just for adding xman's `src` to paths and config `is_pytest` setting
    xman_path = os.path.abspath(os.path.join('src'))
    if xman_path not in sys.path:
        sys.path.insert(0, xman_path)
    config.set__is_pytest(True)


from xman import xman, filesystem
from xman import config
import helper


def test__config():
    config.set__is_pytest(True)
    assert config.is_pytest
    assert config.confirm_off


def test_make_and_remove_dir():
    config.set__is_pytest(True)
    dir_path = '../gitignore/testdir1/testdir2/testdir3'
    xman.make_dir(dir_path)
    assert os.path.exists(dir_path)
    xman.make_dir(dir_path)  # no error on already exists
    dir_path = '../gitignore/testdir1'
    xman.remove_dir(dir_path)
    assert not os.path.exists(dir_path)


def test__make_proj():
    proj = helper.make_proj_from_nothing()
    assert proj.name == 'Test Proj' and xman.proj.descr == 'Test proj descr'


def test__pipeline():
    exp = helper.make_exp_from_nothing().make_pipeline(helper.train, helper.train_params, True).\
        start()
    assert exp.result == helper.train_result


def test__pipeline_with_checkpoints():
    exp = helper.make_exp_from_nothing().make_pipeline_with_checkpoints(
        helper.train_with_mediator, helper.train_params, True).start()
    assert exp.result == helper.train_result
    exp = helper.make_exp_from_nothing().make_pipeline_with_checkpoints(
        helper.train_with_mediator_replace, helper.train_params, True).start()
    assert exp.result == helper.train_result
    exp.delete_checkpoints(need_confirm=False)
    assert not filesystem._has_checkpoints_dir(exp.location_dir)
    exp = helper.make_exp_from_nothing().make_pipeline_with_checkpoints(
        helper.train_with_mediator_custom_path, helper.train_params, True).start()
    assert os.path.exists(os.path.join(exp.location_dir, 'custom/first.cp'))
    assert os.path.exists(os.path.join(exp.location_dir, 'custom/second.cp'))
    exp.delete_checkpoints(need_confirm=False, delete_custom_paths=False)
    assert os.path.exists(os.path.join(exp.location_dir, 'custom/first.cp'))
    assert os.path.exists(os.path.join(exp.location_dir, 'custom/second.cp'))
    exp = helper.make_exp_from_nothing().make_pipeline_with_checkpoints(
        helper.train_with_mediator_custom_path, helper.train_params, True).start()
    exp.delete_checkpoints(need_confirm=False, delete_custom_paths=True)
    assert not os.path.exists(os.path.join(exp.location_dir, 'custom/first.cp'))
    assert not os.path.exists(os.path.join(exp.location_dir, 'custom/second.cp'))


def test__destroy_group():
    config.set__is_pytest(True)
    helper.make_exp_from_nothing()
    xman.destroy_group(1)
    assert xman.proj.num_children == 0


def test__destroy_exp():
    config.set__is_pytest(True)
    helper.make_exp_from_nothing()
    xman.group(1).destroy_exp(1)
    assert xman.group(1).num_children == 0


def test__destroy_exp_after_pipeline_done():
    config.set__is_pytest(True)
    helper.make_exp_from_nothing().make_pipeline(helper.train, helper.train_params, True).start()
    xman.group(1).destroy_exp(1)
    assert xman.group(1).num_children == 0


def test__getting_exp():
    exp = helper.make_exp_from_nothing(num=10)
    assert exp.num == 10
    assert xman.proj.exp(1, 10) is exp
    assert xman.proj.group(1).exp(10) is exp
    assert xman.exp(1, 10) is exp
    assert xman.group(1).exp(10) is exp
    exp = helper.make_exp_from_nothing(num=10)
    assert xman.proj.exp('Test Group', 'Test Exp') is exp
    assert xman.proj.group('Test Group').exp('Test Exp') is exp
    assert xman.exp('Test Group', 'Test Exp') is exp


def test__filesystem_has_checkpoints_dir():
    exp = helper.make_exp_from_nothing()
    xman.make_dir(os.path.join(exp.location_dir, 'checkpoints/'))
    assert filesystem._has_checkpoints_dir(exp.location_dir)
    with pytest.raises(IllegalOperationXManError, match="contains checkpoints folder"):
        exp.start()
