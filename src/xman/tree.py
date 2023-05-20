import os
import re


__tab = '    '
__regex = r'\d+'


def __sort_by_number(name):
    match = re.search(__regex, name)
    return int(match.group()) if match else 0


def __sort_content_by_folders_and_files(target_dir, sort_numbers):
    names = os.listdir(target_dir)
    names = sorted(names, key=__sort_by_number) if sort_numbers else sorted(names)
    dirs = []
    files = []
    for it in names:
        p = os.path.join(target_dir, it)
        if os.path.isdir(p):
            dirs.append(it)
        elif os.path.isfile(p):
            files.append(it)
        else:
            continue
    return dirs, files


def __dirs_part(
        target_dir, depth, current_depth, result, files_limit, files_first, sort_numbers, dirs):
    for d in dirs:
        p = os.path.join(target_dir, d)
        __process_dir(p, depth, current_depth + 1, result, files_limit, files_first, sort_numbers)


def __files_part(target_dir, current_depth, result, files):
    for f in files:
        p = os.path.join(target_dir, f)
        if f.startswith('...'):
            result.append(f"{__tab * (current_depth + 1)}{f}")
            continue
        result.append(f"{__tab * (current_depth + 1)}{os.path.basename(p)}")


def __process_dir(target_dir, depth, current_depth, result, files_limit, files_first, sort_numbers):
    if target_dir.endswith('/'):
        target_dir = target_dir[:-1]
    result.append(f"{__tab * current_depth}{os.path.basename(target_dir) + '/'}")
    if depth is not None and current_depth > depth:
        if len(os.listdir(target_dir)):
            result[-1] += '...'
        return
    dirs, files = __sort_content_by_folders_and_files(target_dir, sort_numbers)
    files_len = len(files)
    if 0 < files_limit < files_len:
        trimmed = files[:2]
        trimmed.append(f"... {files_len - 3} other files are hidden ... ")
        trimmed.append(files[-1])
        files = trimmed
    if files_first:
        __files_part(target_dir, current_depth, result, files)
        __dirs_part(target_dir, depth, current_depth, result, files_limit, files_first, sort_numbers, dirs)
    else:
        __dirs_part(target_dir, depth, current_depth, result, files_limit, files_first, sort_numbers, dirs)
        __files_part(target_dir, current_depth, result, files)


def print_dir_tree(target_dir: str, depth: int = None, files_limit: int = 10,
                   files_first: bool = True, sort_numbers: bool = True):
    print()
    result = []
    __process_dir(target_dir, depth, 0, result, files_limit, files_first, sort_numbers)
    for it in result:
        print(it)
    print()
