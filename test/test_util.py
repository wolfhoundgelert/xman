import pytest

from xman import util
from xman.error import ArgumentsXManError


def test__check_has_value_in_class_public_constants():
    class TestClass:
        CONST1 = 'CONST1'
        CONST2 = 'CONST2'
    util.check_has_value_in_class_public_constants(TestClass.CONST1, TestClass)
    util.check_has_value_in_class_public_constants(TestClass.CONST2, TestClass)
    with pytest.raises(ArgumentsXManError, match=f"Wrong value `{'CONST_THAT_DOES_NOT_EXISTS'}`"):
        util.check_has_value_in_class_public_constants('CONST_THAT_DOES_NOT_EXISTS', TestClass)
