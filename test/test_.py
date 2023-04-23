import os
import sys
import shutil
import pytest

xman_path = os.path.abspath(os.path.join('src'))
if xman_path not in sys.path:
    sys.path.insert(0, xman_path)

import xman
from xman import util


def make_proj_from_nothing(location_dir=None, name=None, descr=None):
    if location_dir is None:
        # location_dir = './gitignore/testproj'  # if running by `pytest` in terminal
        location_dir = '../gitignore/testproj'
    if name is None:
        name = 'Test Proj'
    if descr is None:
        descr = 'Test proj descr'
    shutil.rmtree(location_dir)
    return xman.make_proj(location_dir, name, descr)


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
    with pytest.raises(ValueError, match="`dot_num` should be a string like"):
        util.parse_group_and_exp_num('1.0')
        util.parse_group_and_exp_num('0.1')
        util.parse_group_and_exp_num('dsfsadf')


def test__bug__getting_tenth_exp_with_dotted_num():
    exp = make_exp_from_nothing(num=10)
    assert exp.num == 10
    assert xman.proj.exp('1.10') is exp
    assert xman.proj.group(1).exp(10) is exp



