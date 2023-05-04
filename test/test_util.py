import pytest

from xman import util
from xman.error import ArgumentsXManError
from xman.structbox import ExpStructBoxEvent


def test__check_has_value_in_class_public_constants():
    util.check_has_value_in_class_public_constants(ExpStructBoxEvent.CHILD_MADE, ExpStructBoxEvent)
    util.check_has_value_in_class_public_constants(ExpStructBoxEvent.CHILD_DESTROYED, ExpStructBoxEvent)
    with pytest.raises(ArgumentsXManError, match=f"Wrong value `{'CONST_THAT_DOES_NOT_EXISTS'}`"):
        util.check_has_value_in_class_public_constants('CONST_THAT_DOES_NOT_EXISTS', ExpStructBoxEvent)
