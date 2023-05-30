import sys
import os
import re

from .error import PlatformXManError
from . import filesystem, confirm, maker
from . import util


is_colab = 'google.colab' in sys.modules


def check_colab_forked_folders(exp_struct_box) -> bool:
    """
    Issue with making folders under different Colab accounts in one Google Drive shared folder
    produces folders with duplicated numbers (e.g. `group1` and `group1 (1)`, `exp2` and `exp2 (1)`.
    It happens because there's a 20-second (or even more) lag in update the second account with the
    information about the first one already created a folder with a such number. It can't be solved
    for Colab, but user should be notified for solving the issue manually.
    https://stackoverflow.com/questions/76106194/folders-created-with-python-code-from-2-colab-accounts-in-one-google-drive-share

    Parameter:
        exp_exp_struct_box (ExpStructBox): e.g. ExpProj or ExpGroup instances.

    Returns:
        (bool): `False` if forked folders were found and the response on the input was `No`, `True`
            otherwise.
    """
    if not is_colab:
        raise PlatformXManError(f"Actual only for Google Colab platform!")
    dir_prefix = filesystem.dir_prefix(maker.get_child_class(exp_struct_box))
    regex = fr'^{dir_prefix}\d+ \(\d+\)$'
    folders = []
    for entry in os.scandir(exp_struct_box.location_dir):
        if entry.is_dir() and re.match(regex, entry.name):
            folders.append(entry.name)
    if len(folders):
        loc = exp_struct_box.location_dir
        message = (f"\nFound forked folders {folders} in the location `{loc}`."
                   f"\nIt could be due to a delay in updating one account to the fact that a "
                   f"Google Drive folder was created under a different account: "
                   f"https://stackoverflow.com/questions/76106194/folders-created-with-python-code-"
                   f"from-2-colab-accounts-in-one-google-drive-shareFound"
                   f"\nForked folders are not presented in the project and are essentially lost "
                   f"experiments. You need to process (e.g. rename or delete) them manually."
                   f"\nIn case of frequent occurrence of such a problem, try to take 1 minute "
                   f"pauses between making experiments and groups of experiments under different "
                   f"accounts. Or you can initially create new groups and experiments under only "
                   f"one Colab account, then run and update experiments under different accounts.")
        util.warning(message)
        if not confirm.request(True, f"Leave it as is and proceed?"):
            return False
    return True
