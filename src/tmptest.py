import shutil
import os

from xman import xman


PROJ_DIR = '../gitignore/experiments'


create_new = True

if create_new:
    if os.path.exists(PROJ_DIR):
        shutil.rmtree(PROJ_DIR)
    xman.make_proj(PROJ_DIR, 'Test Project', "Test project descr")
    xman.make_group("Test Group", "Test group descr")
    xman.make_exp(1, "Test Exp", "Test exp descr")
else:
    xman.load_proj(PROJ_DIR)

xman.exp(1, 1).info()
