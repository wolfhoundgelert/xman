import os
import shutil

import xman
from xman.api import ExpProjAPI, ExpGroupAPI, ExpAPI


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


def train(pulse, p1, p2, np1=None, np2=None):
    # print("\ntrain started")
    import time
    # time.sleep(1)
    pulse('ONE')
    # print("train is still in progress...")
    # time.sleep(1)
    pulse('TWO', replace=False)
    # print(f"Pulse checkpoints: `{pulse.intermediate_checkpoints}`, loc dir `{pulse.location_dir}`")
    result = f"p1={p1}, p2={p2}, np1={np1}, np2={np2}"
    # print(f"train finished with result `{result}`")
    return result


train_params = {'p1': 1, 'p2': 2, 'np1': 3, 'np2': 4}

train_result = f"p1={train_params['p1']}, p2={train_params['p2']}, np1={train_params['np1']}, np2={train_params['np2']}"
