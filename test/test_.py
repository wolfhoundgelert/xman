import os
import sys

import pytest

from xman.api import ExpAPI
from xman.error import AlreadyExistsXManError, ArgumentsXManError
from xman.exp import ExpState, Exp


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


def test__change_exp_num():
    exp = helper.make_exp_from_nothing()
    group = exp.group
    group.make_exp('New Exp', 'New exp descr')
    with pytest.raises(AlreadyExistsXManError, match="is already taken by other child"):
        group.change_exp_num(1, 2)
    group.change_exp_num(1, 3)
    assert group.exp(3) is exp


def test__change_group_num():
    group = helper.make_group_from_nothing()
    proj = group.proj
    proj.make_group('New Group', 'New group descr')
    with pytest.raises(AlreadyExistsXManError, match="is already taken by other child"):
        proj.change_group_num(1, 2)
    proj.change_group_num(1, 3)
    assert proj.group(3) is group


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


def test__move_exp():
    exp = helper.make_exp_from_nothing()
    exp.proj.make_group('New Group', 'New group descr')
    xman.proj.move_exp(1, 1, 2, 3)
    assert not xman.group(1).has_exp(1) and xman.group(2).has_exp(3) and xman.group(2).exp(3) is exp


def test__filter_exps_in_group():
    class MockExp(Exp):
        _is_active = True

    group = helper.make_group_from_nothing()
    for i in range(3):
        group.make_exp(f"Exp {i+1}", "Descr")
    exp = xman.exp(1, 2)
    exp._obj.__class__ = MockExp
    actives = group.filter_exps(active=True)
    assert len(actives) == 1 and actives[0] is exp
    xman.exp(1, 1).set_manual_status('DONE', "It's done.")
    manuals = xman.group(1).filter_exps(manual=True)
    assert len(manuals) == 1 and manuals[0] is xman.exp(1, 1)
    all_falses = xman.group(1).filter_exps(active=False, manual=False)
    assert len(all_falses) == 1 and all_falses[0] is xman.exp(1, 3)
    with pytest.raises(ArgumentsXManError, match="nothing to filter"):
        xman.group(1).filter_exps(active=None, manual=None)
    with pytest.raises(ArgumentsXManError, match="Manual experiments can't be active"):
        xman.group(1).filter_exps(active=True, manual=True)


def test__filter_exps_in_proj():
    pass  # TODO
    assert False


def test__filter_exps_in_xman():
    pass  # TODO
    assert False
