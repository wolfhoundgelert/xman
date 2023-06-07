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

def train(p1, p2, np1=None, np2=None):
    print("train started")
    import time
    # time.sleep(2)
    print("train is still in progress...")
    result = f"p1={p1}, p2={p2}, np1={np1}, np2={np2}"
    # time.sleep(2)
    print(f"train finished with result `{result}`")
    return result

params = {
    'p1': 1,
    'p2': 2,
    'np1': 3,
    'np2': 4,
}

xman.exp(1, 1).make_pipeline(train, params).start()

print('\n')
xman.exp(1, 1).info()
print('\n\n')
xman.info()
