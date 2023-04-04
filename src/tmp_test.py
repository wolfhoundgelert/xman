import dill

import xman

proj_dir = '../gitignore/experiments/'

# proj = xman.make_proj(proj_dir, "New Proj", "New Proj descr")
xman.load_proj(proj_dir)

xman.proj.info()
# xman.proj.exp(1.1).success('Everything is ok!')
# xman.proj.exp(1.1).remove_manual_status()
print('\n\n\n')
xman.proj.exp(1.1).info()
