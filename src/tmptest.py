import shutil
import os

# from xman import xman

proj_dir = '../gitignore/experiments'
proj_dir = fr"{proj_dir}"

from pathlib import Path
print(proj_dir)
print(Path(proj_dir).as_posix())
print(Path(proj_dir).resolve().as_posix())

# xman.dir_tree(proj_dir)
#
# create_new = True
# if create_new:
#     if os.path.exists(proj_dir):
#         shutil.rmtree(proj_dir)
#     xman.make_proj(proj_dir, 'Test Project', "This is a test experimental project")
#     xman.proj.make_group("Test Group", "Test group descr")
#     xman.proj.group(1).make_exp("Test Exp", "Test Exp Descr")
# else:
#     xman.load_proj(proj_dir)
#
# xman.dir_tree(proj_dir)
# xman.proj.info()
#
#
#
#
# def train(pulse, p1, p2, np1=None, np2=None):
#     print("train started")
#     import time
#     time.sleep(10)
#     print("train is still in progress...")
#     result = f"p1={p1}, p2={p2}, np1={np1}, np2={np2}"
#     time.sleep(10)
#     print(f"train finished with result `{result}`")
#     return result
#
# params = {
#     'p1': 1,
#     'p2': 2,
#     'np1': 3,
#     'np2': 4,
# }

# xman.proj.exp('1.1').destroy_pipeline().make_pipeline(train, params)
# xman.proj.info()
# xman.proj.exp('1.1').start()
# xman.proj.info()
# print(xman.proj.exp('1.1').result)

# xman.proj.exp(1.1).set_manual_result('DCG@   1: 0.250 | Hits@   1: 0.250\nDCG@   5: 0.316 | Hits@   5: 0.376\nDCG@  10: 0.339 | Hits@  10: 0.448\nDCG@ 100: 0.389 | Hits@ 100: 0.691\nDCG@ 500: 0.419 | Hits@ 500: 0.927\nDCG@1000: 0.427 | Hits@1000: 1.000\n')
# xman.proj.exp('1.1').info()
# xman.proj.info()