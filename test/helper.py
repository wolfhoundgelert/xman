import os
import shutil

from xman import xman
from xman.api import ExpProjAPI, ExpGroupAPI, ExpAPI
from xman.pipeline import CheckpointsMediator


def make_proj_from_nothing(proj_dir=None, name=None, descr=None) -> ExpProjAPI:
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


def make_group_from_nothing(name=None, descr=None, num=None) -> ExpGroupAPI:
    if name is None:
        name = 'Test Group'
    if descr is None:
        descr = 'Test group descr'
    return make_proj_from_nothing().make_group(name, descr, num)


def make_exp_from_nothing(name=None, descr=None, num=None) -> ExpAPI:
    if name is None:
        name = 'Test Exp'
    if descr is None:
        descr = 'Test exp descr'
    return make_group_from_nothing().make_exp(name, descr, num)


def train(p1, p2, np1=None, np2=None):
    result = f"p1={p1}, p2={p2}, np1={np1}, np2={np2}"
    return result


def train_with_mediator(mediator: CheckpointsMediator, p1, p2, np1=None, np2=None):
    mediator.save_checkpoint('first checkpoint', False)
    mediator.save_checkpoint('second checkpoint', False)
    cp_list = mediator.get_checkpoint_paths_list()
    assert len(cp_list) == 2
    assert mediator.load_checkpoint(cp_list[0]) == 'first checkpoint'
    assert mediator.load_checkpoint(cp_list[1]) == 'second checkpoint'
    result = f"p1={p1}, p2={p2}, np1={np1}, np2={np2}"
    return result


def train_with_mediator_replace(mediator: CheckpointsMediator, p1, p2, np1=None, np2=None):
    mediator.save_checkpoint('first checkpoint', True)
    mediator.save_checkpoint('second checkpoint', True)
    cp_list = mediator.get_checkpoint_paths_list()
    assert len(cp_list) == 1
    assert mediator.load_checkpoint(cp_list[0]) == 'second checkpoint'
    result = f"p1={p1}, p2={p2}, np1={np1}, np2={np2}"
    return result


def train_with_mediator_custom_path(mediator: CheckpointsMediator, p1, p2, np1=None, np2=None):
    custom_path = os.path.join(mediator.exp_location_dir, 'custom/first.cp')
    mediator.save_checkpoint('first checkpoint', False, custom_path)
    custom_path = os.path.join(mediator.exp_location_dir, 'custom/second.cp')
    mediator.save_checkpoint('second checkpoint', False, custom_path)
    cp_list = mediator.get_checkpoint_paths_list()
    assert len(cp_list) == 2
    assert mediator.load_checkpoint(cp_list[0]) == 'first checkpoint'
    assert mediator.load_checkpoint(cp_list[1]) == 'second checkpoint'
    result = f"p1={p1}, p2={p2}, np1={np1}, np2={np2}"
    return result


train_params = {'p1': 1, 'p2': 2, 'np1': 3, 'np2': 4}
train_result = f"p1={train_params['p1']}, p2={train_params['p2']}, np1={train_params['np1']}, " \
               f"np2={train_params['np2']}"
