from enum import Enum
from typing import List, Callable

from .error import ArgumentsXManError
from .exp import Exp
from .group import ExpGroup
from .struct import ExpStruct, ExpStructStatus


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


class Mode(Enum):
    AND = 'AND'
    OR = 'OR'


def exps(
        exps: List[Exp],
        # mode: Mode = Mode.AND,
        is_active: bool = None,
        is_manual: bool = None,
        is_ready_for_start: bool = None,
        status_or_list: str | List[str] = None,
        not_status_or_list: str | List[str] = None,
        # TODO Implement:
        str_in_name: str = None,
        str_in_descr: str = None,
        str_in_resolution: str = None,
        has_pipeline: bool = None,
        pipeline_started: bool = None,
        pipeline_error: bool = None,
        pipeline_finished: bool = None,
        has_manual_result: bool = None,
        has_pipeline_result: bool = None,
        has_result: bool = None,
        custom_filter_or_list: Callable[[Exp], bool] | List[Callable[[Exp], bool]] = None,
        # TODO custom filter: lambda exp: exp.parent == xman.group(1)
) -> List[Exp]:
    result = exps if mode == Mode.AND else []
    if is_active is not None:
        result = [x for x in result if x.is_active == is_active]
    if is_manual is not None:
        result = [x for x in result if x.is_manual == is_manual]
    if is_ready_for_start is not None:
        result = [x for x in result if x.is_ready_for_start == is_ready_for_start]
    if status_or_list is not None:
        status_list = [status_or_list] if type(status_or_list) != list else status_or_list
        for status in status_list:
            if not ExpStructStatus.has_status(status):
                raise ArgumentsXManError(
                    f"Wrong `status_or_list` param: statuses should be from the workflow "
                    f"`{ExpStructStatus.workflow}`, but `{status_or_list}` was given!")
        result = [x for x in result if x.status in status_list]
    if not_status_or_list is not None:
        not_status_list = [not_status_or_list] if type(not_status_or_list) != list \
            else not_status_or_list
        for status in not_status_list:
            if not ExpStructStatus.has_status(status):
                raise ArgumentsXManError(
                    f"Wrong `status_or_list` param: statuses should be from the workflow "
                    f"`{ExpStructStatus.workflow}`, but `{not_status_or_list}` was given!")
        result = [x for x in result if x.status not in not_status_list]
    return exps.copy() if result is exps else result


def groups(groups: List[ExpGroup]):
    pass  # TODO


# TODO Do I really need this below?

# TODO Implement xman.filter(xman.filter.Query.EXP_WITH_PIPELINE or 'EXP_WITH_PIPELINE')
#   or xman.filter(['EXP', 'DONE', 'MANUAL_STATUS'], 'OR' or 'AND') or xman.filter.Mode.OR.
#   Or maybe it's better use tuples (Query, Mode) to describe modes for any queries?

class Query:

    EXP = 'EXP'
    GROUP = 'GROUP'

    EMPTY = 'EMPTY'
    TODO = 'TODO'
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'
    SUCCESS = 'SUCCESS'
    FAIL = 'FAIL'

    ACTIVE = 'ACTIVE'
    IDLE = 'IDLE'
    UNKNOWN = 'UNKNOWN'

    AUTO_STATUS = 'AUTO_STATUS'
    MANUAL_STATUS = 'MANUAL_STATUS'

    PIPELINE = 'PIPELINE'
    NO_PIPELINE = 'NO_PIPELINE'

    RESULT = 'RESULT'
    NO_RESULT = 'NO_RESULT'


class Mode:

    AND = 'AND'
    OR = 'OR'

    # TODO how to add these?
    IS = 'IS'  # default
    NOT = 'NOT'
    EXC = 'EXC'  # Any from the category except this, it's equal to NOT


def filter_entities(query: str | List[str], mode: str) -> List[ExpStruct]:  # TODO or tuples of (Query, Mode)
    pass  # TODO
