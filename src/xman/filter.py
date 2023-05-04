# TODO Implement xman.filter(xman.filter.Query.EXP_WITH_PIPELINE or 'EXP_WITH_PIPELINE')
#   or xman.filter(['EXP', 'DONE', 'MANUAL_STATUS'], 'OR' or 'AND') or xman.filter.Mode.OR.
#   Or maybe it's better use tuples (Query, Mode) to describe modes for any queries?
from .struct import ExpStruct


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



def filter(query: str | [str], mode: str) -> [ExpStruct]:  # TODO or tuples of (Query, Mode)
    pass  # TODO
