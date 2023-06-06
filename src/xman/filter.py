from typing import List, Callable

from .error import ArgumentsXManError
from .struct import ExpStructStatus


def intersect(*lists):
    if not lists:
        return []
    intersection_set = set(lists[0])
    for lst in lists[1:]:
        intersection_set.intersection_update(lst)
    return list(intersection_set)


def unite(*lists):
    merged_list = []
    for lst in lists:
        merged_list.extend(lst)
    return list(set(merged_list))


def __check_and_get_status_list(status_or_list):
    lst = status_or_list if type(status_or_list) == list else [status_or_list]
    for status in lst:
        if not ExpStructStatus.has_status(status):
            raise ArgumentsXManError(
                f"Wrong `status_or_list` param - statuses should be from the workflow "
                f"`{ExpStructStatus.workflow}`, but `{status_or_list}` was given!")
    return lst


def __exp_key(exp): return exp.group.num, exp.num
def __group_key(group): return group.num


class Mode:

    AND = 'AND'
    OR = 'OR'

    @staticmethod
    def _check_mode(mode):
        if mode != Mode.AND and mode != Mode.OR:
            ArgumentsXManError(
                f"`mode` should be 'AND' or 'OR' string, but `{mode}` was given!")


def exps(
        exps: List['Exp'],
        mode: str = 'AND',
        custom_filter: Callable[['Exp'], bool] = None,
        is_active: bool = None,
        is_manual: bool = None,
        is_ready_for_start: bool = None,
        status_or_list: str | List[str] = None,
        not_status_or_list: str | List[str] = None,
        # TODO Implement:
        # str_in_name: str = None,
        # str_in_descr: str = None,
        # str_in_resolution: str = None,
        # has_pipeline: bool = None,
        # pipeline_started: bool = None,
        # pipeline_error: bool = None,
        # pipeline_finished: bool = None,
        # has_manual_result: bool = None,
        # has_pipeline_result: bool = None,
        # has_result: bool = None,
) -> List['Exp']:
    Mode._check_mode(mode)
    results = []
    if custom_filter is not None:
        results.append([x for x in exps if custom_filter(x)])
    if is_active is not None:
        results.append([x for x in exps if x.is_active == is_active])
    if is_manual is not None:
        results.append([x for x in exps if x.is_manual == is_manual])
    if is_ready_for_start is not None:
        results.append([x for x in exps if x.is_ready_for_start == is_ready_for_start])
    if status_or_list is not None:
        status_list = __check_and_get_status_list(status_or_list)
        results.append([x for x in exps if x.status_str in status_list])
    if not_status_or_list is not None:
        not_status_list = __check_and_get_status_list(not_status_or_list)
        results.append([x for x in exps if x.status_str not in not_status_list])
    result = intersect(*results) if mode == Mode.AND else unite(*results)
    return sorted(result, key=__exp_key)


def groups(
        groups: List['ExpGroup'],
        mode: str = 'AND',
        custom_filter: Callable[['ExpGroup'], bool] = None,
        status_or_list: str | List[str] = None,
        not_status_or_list: str | List[str] = None,
) -> List['ExpGroup']:
    Mode._check_mode(mode)
    results = []
    if custom_filter is not None:
        results.append([x for x in groups if custom_filter(x)])
    if status_or_list is not None:
        status_list = __check_and_get_status_list(status_or_list)
        results.append([x for x in groups if x.status_str in status_list])
    if not_status_or_list is not None:
        not_status_list = __check_and_get_status_list(not_status_or_list)
        results.append([x for x in groups if x.status_str not in not_status_list])
    result = intersect(*results) if mode == Mode.AND else unite(*results)
    return sorted(result, key=__group_key)
