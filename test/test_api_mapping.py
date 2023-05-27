"""
def check_api(class_one, class_two, excluding_list=None, including_list=None) -> Tuple[List, List]:

- Check only public methods and properties, that everything exists in both classes.
- For each pair check that signatures are the same.
- Excluding list for public methods and properties that not needed to check.
- Including list for adding protected methods and properties for the check.

Returns: absentee list and list with difference in signatures
"""

from typing import Tuple, List


def get_public_members() -> List[str]:
    pass  # TODO


def check_api(class_one, class_two,
              excluding_list=None, including_list=None) -> Tuple[List[str], List[str]]:
    pass  # TODO


def test__get_public_members():
    pass  # TODO


def test__check_api():
    pass  # TODO


def test__ExpStructAPI():
    pass  # TODO


def test__ExpAPI():
    pass  # TODO


def test__ExpGroupAPI():
    pass  # TODO


def test__ExpProjAPI():
    pass  # TODO


def test__XManAPI():
    pass  # TODO
