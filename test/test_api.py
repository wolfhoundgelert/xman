"""
def check_api(class_one, class_two, excluding_list=None, including_list=None) -> Tuple[List, List]:

- Check only public methods and properties, that everything exists in both classes.
- For each pair check that signatures are the same.
- Excluding list for public methods and properties that not needed to check.
- Including list for adding protected methods and properties for the check.

Returns: absentee list and list with difference in signatures
"""
import inspect
from typing import Tuple, List, Callable, Optional
import re
import pytest

from xman import XManAPI
from xman.api import ExpAPI, ExpStructAPI, ExpGroupAPI, ExpProjAPI
from xman.error import ArgumentsXManError
from xman.exp import Exp
from xman.group import ExpGroup
from xman.proj import ExpProj
from xman.struct import ExpStruct


def get_public_members(cls) -> List[str]:
    return [member for member in dir(cls) if not member.startswith(('_', '__'))]


def get_normalized_signature_str(member: Callable | property) -> str:
    sig = str(inspect.signature(member))
    sig = re.sub(r'\bxman\.\w+\.Exp', 'Exp', sig)
    sig = re.sub(r'\b(Exp\w*)API\b', r'\1', sig)
    sig = re.sub(r"'", '', sig)
    return sig


def is_equal_signatures(member_one: Callable | property, member_two: Callable | property) -> bool:
    one_exists = member_one is not None
    two_exists = member_two is not None
    if not one_exists and not two_exists:
        raise ArgumentsXManError(
            f"Both `member_one` and `member_two` are None - shouldn't be like that!")
    if one_exists != two_exists:
        return False
    one_is_prop = isinstance(member_one, property)
    two_is_prop = isinstance(member_two, property)
    if one_is_prop != two_is_prop:
        return False
    if one_is_prop:
        one_has_setter = member_one.fset is not None
        two_has_setter = member_two.fset is not None
        if one_has_setter != two_has_setter:
            return False
        if one_has_setter and \
                get_normalized_signature_str(member_one.fset) != \
                get_normalized_signature_str(member_two.fset):
            return False
        return get_normalized_signature_str(member_one.fget) == \
            get_normalized_signature_str(member_two.fget)
    else:
        return get_normalized_signature_str(member_one) == \
            get_normalized_signature_str(member_two)


# TODO Add checking on annotation and returning value if returns smt
def check_api(class_one, class_two, excluding_list: List[str] = None,
              including_list: List[str] = None) -> Optional[Tuple[str, List[str], List[str]]]:
    one_set = set(get_public_members(class_one))
    two_set = set(get_public_members(class_two))
    excluding_set = set([] if excluding_list is None else excluding_list)
    including_set = set([] if including_list is None else including_list)
    if len(cross_set := excluding_set & including_set) > 0:
        raise ArgumentsXManError(
            f"Members {cross_set} can't be in both `excluding_list` and `including_list")
    for member in (excluding_set | including_set) - (one_set | two_set):
        if not hasattr(class_one, member) and not hasattr(class_two, member):
            raise ArgumentsXManError(
                f"Member `{member}` doesn't exist neither in `{class_one}` or `{class_two}")
    existence_diff_set = (one_set ^ two_set) - excluding_set
    common_set = (one_set & two_set) - excluding_set
    for member in including_set:
        one_has = hasattr(class_one, member)
        two_has = hasattr(class_two, member)
        if one_has == two_has == False:
            raise ArgumentsXManError(
                f"`{member}` doesn't exist in either `class_one` or `class_two`!")
        elif one_has == two_has == True:
            common_set.add(member)
        else:
            existence_diff_set.add(member)
    signatures_diff_set = set()
    for member in common_set:
        is_equal = is_equal_signatures(getattr(class_one, member), getattr(class_two, member))
        if not is_equal:
            signatures_diff_set.add(member)
    if len(existence_diff_set) or len(signatures_diff_set):
        not_exist = []
        for it in existence_diff_set:
            it_str = f"{(class_two if it in one_set else class_one).__name__}:{it}"
            not_exist.append(it_str)
        signatures = list(signatures_diff_set)
        info = f"\n\nAPI CHECKING REPORT:\nNot exist: {not_exist}\n" \
               f"Different signatures: {signatures}\n"
        return info, list(existence_diff_set), signatures
    return None


def test__get_public_members():
    class A:
        @staticmethod
        def sm(): pass
        @staticmethod
        def _sm(): pass
        @staticmethod
        def __sm(): pass

        @property
        def p(self): pass
        @property
        def _p(self): pass
        @property
        def __p(self): pass

        def m(self): pass
        def _m(self): pass
        def __m(self): pass

    lst = get_public_members(A)
    assert len(lst) == 3 and set(lst) == set(['sm', 'p', 'm'])


def test__get_normalized_signature_str():
    def foo(param1: ExpStructAPI, param2: ExpAPI) -> ExpGroupAPI: pass
    def bar(param1: ExpStruct, param2: Exp) -> ExpGroup: pass
    def biz(param1: ExpStructAPI, param2: ExpProjAPI) -> ExpGroupAPI: pass
    assert get_normalized_signature_str(foo) == get_normalized_signature_str(bar)
    assert get_normalized_signature_str(biz) != get_normalized_signature_str(bar)


def test__is_equal_signatures():
    def a(): pass
    def b(): pass
    assert is_equal_signatures(a, b)

    def a(): pass
    def b() -> bool: pass
    assert not is_equal_signatures(a, b)

    def a(): pass
    def b(foo: int): pass
    assert not is_equal_signatures(a, b)

    def a(bar: int): pass
    def b(foo: int): pass
    assert not is_equal_signatures(a, b)

    def a(foo: int): pass
    def b(foo: int): pass
    assert is_equal_signatures(a, b)

    class A:
        @property
        def foo(self): pass
        @foo.setter
        def foo(self, value): pass

        @property
        def bar(self): pass
        @bar.setter
        def bar(self, value): pass

        @property
        def biz(self): pass
        @bar.setter
        def biz(self, value): pass

    class B:
        @property
        def foo(self): pass
        @foo.setter
        def foo(self, value): pass

        @property
        def bar(self): pass
        @bar.setter
        def bar(self, value) -> bool: pass

        @property
        def biz(self): pass

    assert is_equal_signatures(A.foo, B.foo)
    assert not is_equal_signatures(A.bar, B.bar)
    assert not is_equal_signatures(A.biz, B.biz)
    assert not is_equal_signatures(A.foo, None)
    with pytest.raises(ArgumentsXManError, match="are None"):
        is_equal_signatures(None, None)


def test__check_api():
    class A:
        @staticmethod
        def sm(): pass
        @property
        def p(self): pass
        def m(self, param: int): pass
        def foo(self): pass
        def _bar(self) -> str: pass

    class B:
        @staticmethod
        def sm(): pass
        def m(self, param: str): pass
        def _bar(self, param: bool) -> str: pass

    info, existence_diff, signatures_diff = check_api(A, B, ['foo'], ['_bar'])
    assert info is not None
    assert set(existence_diff) == set(['p'])
    assert set(signatures_diff) == set(['m', '_bar'])


def test__ExpStruct():
    excludes = ['parent', 'api']
    result = check_api(ExpStruct, ExpStructAPI, excludes)
    if result is not None:
        info, _, _ = result
        print(info)
        assert False


def test__Exp():
    excludes = ['parent', 'api']
    result = check_api(Exp, ExpAPI, excludes)
    if result is not None:
        info, _, _ = result
        print(info)
        assert False


def test__ExpGroup():
    excludes = ['parent', 'api', 'make_child', 'has_child', 'num_children', 'change_child_num',
                'children_nums', 'child', 'children', 'delete_child', 'children_names']
    result = check_api(ExpGroup, ExpGroupAPI, excludes)
    if result is not None:
        info, _, _ = result
        print(info)
        assert False


def test__ExpProj():
    excludes = ['parent', 'api', 'make_child', 'has_child', 'num_children', 'change_child_num',
                'children_nums', 'child', 'children', 'delete_child', 'children_names']
    result = check_api(ExpProj, ExpProjAPI, excludes)
    if result is not None:
        info, _, _ = result
        print(info)
        assert False


def test__ExpProjAPI_vs_XManAPI():
    excludes = ['move_exp', 'delete_dir', 'is_manual', 'name', 'make_dir', 'rename_or_move_dir',
                'num_groups', 'descr', 'num_exps', 'note', 'dir_tree', 'make_proj', 'num',
                'set_manual_status', 'groups_nums', 'result_viewer', 'load_proj', 'edit', 'fail',
                'reload', 'exps_names', 'exps_nums', 'proj', 'status', 'success', 'tree',
                'delete_manual_status', 'groups_names', 'change_group_num', 'result_stringifier']
    result = check_api(ExpProjAPI, XManAPI, excludes)
    if result is not None:
        info, _, _ = result
        print(info)
        assert False
