from .proj import ExpProj
from .group import ExpGroup
from . import util
import sys
import os
import re


is_colab = 'google.colab' in sys.modules


def check_forked_folders(target: ExpProj | ExpGroup):
    """
    Issue with making folders under different Colab accounts in one Google Drive shared folder produces folders with
    duplicated numbers (e.g. '`group1`' and '`group1 (1)`', '`exp2`' and '`exp2 (1)`'. It happens because there's a
    20-second (or even more) lag in update the second account with the information about the first one already created
    a folder with a such number. It can't be solved for Colab, but user should be notified for solving the issue
    manually.
    """
    if not is_colab:
        return True
    dir_prefix = target._get_child_class()._dir_prefix()
    regex = fr'^{dir_prefix}\d+ \(\d+\)$'
    folders = []
    for entry in os.scandir(target.location_dir):
        if entry.is_dir() and re.match(regex, entry.name):
            folders.append(entry.name)
    if len(folders):
        message = f"Found forked folders {folders} in the location `{target.location_dir}`. It could be due to a " \
                  f"delay in updating one account to the fact that a Google Drive folder was created under a " \
                  f"different account. Forked folders are not presented in the project and are essentially lost " \
                  f"experiments. You need to process (e.g. rename or delete) them manually. In case of frequent " \
                  f"occurrence of such a problem, try to take 1 minute pauses between making experiments and groups " \
                  f"of experiments under different accounts. Or you can initially create new groups and experiments " \
                  f"under only one Colab account, then run and update experiments under different accounts."
        util.warning(message)
        if not util.response(f"Leave it as is and proceed?"):
            return False
    if isinstance(target, ExpProj):
        for group in target.groups():
            if not check_forked_folders(group):
                return False
    return True
