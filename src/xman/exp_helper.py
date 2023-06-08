from typing import Union

from . import util


def get_info_with_marked_exps(box: Union['ExpProj', 'ExpGroup']) -> str:
    from .proj import ExpProj
    text = super(type(box), box).info()
    lst = box.filter_exps(has_marker=True)
    mark_num = util.TAB_NUM_SPACES * (2 if isinstance(box, ExpProj) else 1) - 1
    mark = '>' * mark_num
    for exp in lst:
        exp_str = str(exp)
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if exp_str in line:
                lines[i] = mark + line[mark_num:]
                break
        text = '\n'.join(lines)
    return text
