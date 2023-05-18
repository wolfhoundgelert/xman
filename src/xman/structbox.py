from typing import Optional

from .error import ArgumentsXManError, NotExistsXManError, AlreadyExistsXManError, \
    IllegalOperationXManError
from .struct import ExpStruct, ExpStructStatus
from . import util, confirm
from . import maker
from . import filesystem


class ExpStructBox(ExpStruct):

    @property
    def _num_children(self):
        return len(self._children())

    def _process_auto_status(self):
        resolution = ExpStruct._AUTO_STATUS_RESOLUTION
        if self.__children_has_status(ExpStructStatus.ERROR, False):
            status = ExpStructStatus.ERROR
        elif self.__children_has_status(ExpStructStatus.IN_PROGRESS, False):
            status = ExpStructStatus.IN_PROGRESS
        elif self.__children_has_status(ExpStructStatus.EMPTY, True):
            status = ExpStructStatus.EMPTY
        elif self.__children_has_status(ExpStructStatus.TODO, True):
            status = ExpStructStatus.TODO
        elif self.__children_has_status(ExpStructStatus.DONE, True):
            status = ExpStructStatus.DONE
        elif self.__children_has_status(ExpStructStatus.SUCCESS, True):
            status = ExpStructStatus.SUCCESS
        elif self.__children_has_status(ExpStructStatus.FAIL, True):
            status = ExpStructStatus.FAIL
        elif self.__children_has_status([ExpStructStatus.EMPTY, ExpStructStatus.TODO], True):
            status = ExpStructStatus.TODO
        elif self.__children_has_status([ExpStructStatus.DONE, ExpStructStatus.SUCCESS,
                                         ExpStructStatus.FAIL], True):
            status = ExpStructStatus.DONE
        else:
            status = ExpStructStatus.IN_PROGRESS
        return status, resolution

    def _update(self):
        if self.__updating:
            return
        self.__updating = True
        super()._update()
        nums = filesystem._get_children_nums(self)
        for num in nums:
            if num not in self.__num_to_child:
                child = maker._recreate_child(self, num)
                self.__attention__add(child)
        for child in self._children():
            if child._num not in nums:
                self.__attention__remove(child)
        for name in list(self.__name_to_child.keys()):
            del self.__name_to_child[name]
        for child in self._children():
            child._update()
            self.__name_to_child[child._data.name] = child
        # Status should be updated at the end of the inherited updating hierarchy
        if type(self) == ExpStructBox:
            self._update_status()
        self.__updating = False

    def _has_child_num_or_name(self, num_or_name):
        if util.is_num(num_or_name):
            return num_or_name in self.__num_to_child
        elif util.is_name(num_or_name):
            return num_or_name in self.__name_to_child
        else:
            raise ArgumentsXManError(f"`num_or_name` should be num >= 1 (int) or name (str), "
                                     f"but `{num_or_name}` was given!")

    def _get_child_by_num_or_name(self, num_or_name):
        if util.is_num(num_or_name) and num_or_name in self.__num_to_child:
            return self.__num_to_child[num_or_name]
        elif util.is_name(num_or_name) and num_or_name in self.__name_to_child:
            return self.__name_to_child[num_or_name]
        raise NotExistsXManError(f"There's no child with num or name `{num_or_name}` "
                                 f"in the `{self}`!")

    def _make_child(self, name, descr, num=None) -> ExpStruct:
        util.check_num(num, True)
        if self._has_child_num_or_name(name):
            raise AlreadyExistsXManError(
                f"A child with the name `{name}` already exists in the `{self}`!")
        if num is not None:
            if self._has_child_num_or_name(num):
                raise AlreadyExistsXManError(
                    f"A child with the num `{num}` already exists in the `{self}`!")
        else:
            nums = filesystem._get_children_nums(self)
            max_num = max(nums) if len(nums) else 0
            num = max_num + 1
        child = maker._make_new_child(self, name, descr, num)
        if child is not None:
            self.__attention__add(child)
        return child

    def _destroy_child(self, num_or_name, need_confirm=True):
        child = self._get_child_by_num_or_name(num_or_name)
        if confirm._remove_struct_and_all_its_content(child, need_confirm):
            self.__attention__remove(child)
            maker._destroy_child(child)

    def _children(self):
        return list(self.__num_to_child.values())

    def _nums(self):
        return list(self.__num_to_child.keys())

    def _names(self):
        return list(self.__name_to_child.keys())

    def _get_child_by_auto_status(self, status_or_list) -> Optional[ExpStruct]:
        sl = status_or_list if type(status_or_list) is list else [status_or_list]
        for status in sl:
            for child in self._children():
                if not child._is_manual and child._status.status == status:
                    return child
        return None

    def _info(self):
        text = super()._info()
        for child in self._children():
            text += util.tab(f"\n\n{child._info()}")
        return text

    def _change_child_num(self, num_or_name, new_num):
        child = self._get_child_by_num_or_name(num_or_name)
        if self._has_child_num_or_name(new_num):
            raise AlreadyExistsXManError(f"Can't change number to `{new_num}` for `{child}` - "
                                            f"new number is already taken by other child!")
        dir_path = child._location_dir
        child_dir_pattern = filesystem._dir_prefix(maker._get_child_class(self))
        new_path = filesystem._change_num_in_path_by_pattern(dir_path, child_dir_pattern, new_num)
        filesystem.rename_or_move_dir(dir_path, new_path)
        self.__attention__remove(child)
        # Also changes `num` as it's processing from the path:
        child._ExpStruct__attention__change_location_dir(new_path)
        self.__attention__add(child)

    def _destroy(self):
        for num in list(self.__num_to_child.keys()):
            self._destroy_child(num, False)
        self.__num_to_child = None
        self.__name_to_child = None
        super()._destroy()

    def __init__(self, location_dir, parent):
        self.__num_to_child = {}
        self.__name_to_child = {}
        self.__updating = False
        super().__init__(location_dir, parent)

    def __children_has_status(self, status_or_list, all_children: bool):
        sl = status_or_list if type(status_or_list) is list else [status_or_list]
        for child in self._children():
            s = child._status.status
            if all_children:
                if s not in sl:
                    return False
            else:
                if s in sl:
                    return True
        return True if all_children else False

    def __attention__add(self, child):
        self.__num_to_child[child._num] = child
        self.__name_to_child[child._data.name] = child

    def __attention__remove(self, child):
        del self.__num_to_child[child._num]
        del self.__name_to_child[child._data.name]
