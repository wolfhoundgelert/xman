# TODO filter.exps() and filter.groups()

from xman import xman
import helper


def test__sorted_exps():
    helper.make_proj_from_nothing()
    xman.make_group('G1', 'G1 descr')
    e1 = xman.make_exp('G1', 'G1 E1', 'G1 E1 descr')
    e2 = xman.make_exp('G1', 'G1 E2', 'G1 E2 descr')
    xman.make_group('G2', 'G2 descr')
    e3 = xman.make_exp('G2', 'G2 E1', 'G2 E1 descr')
    e4 = xman.make_exp('G2', 'G2 E2', 'G2 E2 descr')
    exps = xman.exps()
    assert exps == [e1, e2, e3, e4]


def test__sorted_groups():
    helper.make_proj_from_nothing()
    g1 = xman.make_group('G1', 'G1 descr')
    g2 = xman.make_group('G2', 'G2 descr')
    groups = xman.groups()
    assert groups == [g1, g2]

