import xman

proj_dir = '../gitignore/experiments/'

# proj = xman.make_proj(proj_dir, "New Proj", "New Proj descr")
proj = xman.load_proj(proj_dir)

# proj.make_group('New Group', 'New Group descr')
# proj.make_exp(1, 'New Exp', 'New Exp descr')

# print(proj.exp(1.1)

proj.exp(1.1).info()


