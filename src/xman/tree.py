import os


def __sort_content_by_folders_and_files(target_dir):
    ld = sorted(os.listdir(target_dir))
    dirs = []
    files = []
    for it in ld:
        p = os.path.join(target_dir, it)
        if os.path.isdir(p):
            dirs.append(it)
        elif os.path.isfile(p):
            files.append(it)
        else:
            continue
    return dirs, files


def __process_dir(target_dir, depth, result):
    tab = '    '
    if target_dir.endswith('/'):
        target_dir = target_dir[:-1]
    result.append(f"{tab * depth}{os.path.basename(target_dir) + '/'}")
    dirs, files = __sort_content_by_folders_and_files(target_dir)
    l = len(files)
    if l > 10:
        trimmed = files[:2]
        trimmed.append(f"... {l - 3} other files are hidden ... ")
        trimmed.append(files[-1])
        files = trimmed
    for f in files:
        p = os.path.join(target_dir, f)
        if f.startswith('...'):
            result.append(f"{tab * (depth + 1)}{f}")
            continue
        result.append(f"{tab * (depth + 1)}{os.path.basename(p)}")
    for d in dirs:
        p = os.path.join(target_dir, d)
        __process_dir(p, depth + 1, result)


def _print_dir_tree(target_dir):
    print()
    result = []
    __process_dir(target_dir, 0, result)
    for it in result:
        print(it)
    print()
