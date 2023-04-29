import pytest
import os
import sys
import shutil

from xman.error import ArgumentsXManError

xman_path = os.path.abspath(os.path.join('src'))
if xman_path not in sys.path:
    sys.path.insert(0, xman_path)

import xman
from xman import util


def make_proj_from_nothing(proj_dir=None, name=None, descr=None):
    if proj_dir is None:
        # proj_dir = './gitignore/testproj'  # if running by `pytest` in terminal
        proj_dir = '../gitignore/testproj'
    if name is None:
        name = 'Test Proj'
    if descr is None:
        descr = 'Test proj descr'
    if os.path.exists(proj_dir):
        shutil.rmtree(proj_dir)
    return xman.make_proj(proj_dir, name, descr)


def make_group_from_nothing(name=None, descr=None, num=None):
    if name is None:
        name = 'Test Group'
    if descr is None:
        descr = 'Test group descr'
    return make_proj_from_nothing().make_group(name, descr, num)


def make_exp_from_nothing(name=None, descr=None, num=None):
    if name is None:
        name = 'Test Exp'
    if descr is None:
        descr = 'Test exp descr'
    return make_group_from_nothing().make_exp(name, descr, num)


def test__make_proj():
    proj = make_proj_from_nothing()
    assert proj.name == 'Test Proj' and xman.proj.descr == 'Test proj descr'


def test__parse_group_and_exp_num():
    assert 1, 1 == util.parse_group_and_exp_num('1.1')
    assert 1, 10 == util.parse_group_and_exp_num('1.10')
    with pytest.raises(ArgumentsXManError, match="`dot_num` should be a string like"):
        util.parse_group_and_exp_num('1.0')
        util.parse_group_and_exp_num('0.1')
        util.parse_group_and_exp_num('dsfsadf')


def test__bug__getting_tenth_exp_with_dotted_num():
    exp = make_exp_from_nothing(num=10)
    assert exp.num == 10
    assert xman.proj.exp('1.10') is exp
    assert xman.proj.group(1).exp(10) is exp


def test__bug__exp_broken_after_setting_wrong_status():
    exp = make_exp_from_nothing()
    with pytest.raises(ArgumentsXManError, match="doesn't have status"):
        exp.set_manual_status('FAILED', "There's no `FAILED` status - should be `FAIL`")
    assert exp.status.status == 'EMPTY'
    exp.set_manual_status('FAIL', "Acceptable status")
    assert exp.status.status == 'FAIL'


def test__bug__exp_struct_box_set_manual_status_doesnt_work_after_exp_wrong_status_setting():
    exp = make_exp_from_nothing()
    try:
        exp.set_manual_status('FAILED', "There's no `FAILED` status - should be `FAIL`")
    except:
        pass
    xman.proj.set_manual_status('TODO', None)
    assert xman.proj.status.status == 'TODO'
    xman.proj.group(1).set_manual_status('TODO', None)
    assert xman.proj.group(1).status.status == 'TODO'


def test__bug__wrong_proj_status():
    exp = make_exp_from_nothing()
    exp.set_manual_status('SUCCESS', 'Success')
    proj = xman.proj
    group = proj.group(1)
    group.make_exp('Lowercase', 'Lowercase input')
    assert group.status.status == 'IN_PROGRESS'
    assert proj.status.status == 'IN_PROGRESS'
