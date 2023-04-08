import xman

proj_dir = '../gitignore/experiments/'

create_new = False
if create_new:
    xman.make_proj(proj_dir, 'Test Project', "This is a test experimental project")
    xman.proj.make_group("Test Group", "Test group descr")
    xman.proj.group(1).make_exp("Test Exp", "Test Exp Descr")
else:
    xman.load_proj(proj_dir)

xman.dir_tree(proj_dir)
xman.proj.info()

def train(pulse, p1, p2, np1=None, np2=None):
    print("train in progress...")
    result = f"p1={p1}, p2={p2}, np1={np1}, np2={np2}"
    return result

params = {
    'p1': 1,
    'p2': 2,
    'np1': 3,
    'np2': 4,
}

xman.proj.exp(1.1).remove_pipeline().attach_pipeline(train, params)
xman.proj.exp(1.1).start()
xman.proj.info()