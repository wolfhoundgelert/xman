import os
import shutil

from . import util
from .error import ArgumentsXManError, NotExistsXManError, AlreadyExistsXManError
from .struct import ExpStructEvent, ExpStruct, ExpStructStatus


class ExpStructBoxEvent(ExpStructEvent):

    MAKE_CHILD = 'MAKE_CHILD'
    DESTROY_CHIlD = 'DESTROY_CHIlD'


class ExpStructBox(ExpStruct):

    def __init__(self, location_dir, name, descr):
        self.__num_to_child = {}
        self.__name_to_child = {}
        self.__updating = False
        super().__init__(location_dir, name, descr)

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

    def __add(self, child):
        self.__num_to_child[child.num] = child
        self.__name_to_child[child._data.name] = child
        child._add_listener(ExpStructEvent, self._ExpStructEvent_listener)
        if isinstance(child, ExpStructBox):
            child._add_listener(ExpStructBoxEvent, self._ExpStructBoxEvent_listener)

    def __remove(self, child):
        del self.__num_to_child[child.num]
        del self.__name_to_child[child._data.name]
        child._remove_listener(ExpStructEvent, self._ExpStructEvent_listener)
        if isinstance(child, ExpStructBox):
            child._remove_listener(ExpStructBoxEvent, self._ExpStructBoxEvent_listener)
        child._destroy()

    def _get_child_class(self): util.override_it()

    def _get_child_dir(self, num):
        return os.path.join(self.location_dir, self._get_child_class()._dir_prefix() + str(num))

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
        elif self.__children_has_status([ExpStructStatus.DONE, ExpStructStatus.SUCCESS, ExpStructStatus.FAIL], True):
            status = ExpStructStatus.DONE
        else:
            status = ExpStructStatus.IN_PROGRESS
        return status, resolution

    def _update(self):
        if self.__updating:
            return
        self.__updating = True
        super()._update()
        child_class = self._get_child_class()
        child_dir_prefix = child_class._dir_prefix()
        nums = util.get_dir_nums_by_pattern(self.location_dir, child_dir_prefix)
        for num in nums:
            if num not in self.__num_to_child:
                location_dir = self._get_child_dir(num)
                child = child_class(location_dir, None, None)
                self.__add(child)
        for child in self._children():
            if child.num not in nums:
                self.__remove(child)
        for name in list(self.__name_to_child.keys()):
            del self.__name_to_child[name]
        for child in self._children():
            self.__name_to_child[child._data.name] = child
            child._update()
        # Status should be updated at the end of the inherited updating hierarchy
        if type(self) == ExpStructBox:
            self._update_status()
        self.__updating = False

    def _has_child_num_or_name(self, num_or_name):
        self._update()
        if util.is_num(num_or_name):
            return num_or_name in self.__num_to_child
        elif util.is_name(num_or_name):
            return num_or_name in self.__name_to_child
        else:
            raise ArgumentsXManError(f"`num_or_name` should be num >= 1 (int) or name (str), but `{num_or_name}` was given!")

    def _get_child_by_num_or_name(self, num_or_name):
        self._update()
        if util.is_num(num_or_name) and num_or_name in self.__num_to_child:
            return self.__num_to_child[num_or_name]
        elif util.is_name(num_or_name) and num_or_name in self.__name_to_child:
            return self.__name_to_child[num_or_name]
        raise NotExistsXManError(f"There's no item with num or name `{num_or_name}`!")

    def _get_child_highest_num(self):
        self._update()
        nums = self.__num_to_child.keys()
        return max(nums) if len(nums) else 0

    def _make_child(self, name, descr, num=None) -> ExpStruct:
        self._update()
        util.check_num(num, True)
        if self._has_child_num_or_name(name):
            raise AlreadyExistsXManError(f"A child with the name `{name}` already exists!")
        if num is not None:
            if self._has_child_num_or_name(num):
                raise AlreadyExistsXManError(f"A child with the num `{num}` already exists!")
        else:
            num = self._get_child_highest_num() + 1
        child_dir = self._get_child_dir(num)
        child_class = self._get_child_class()
        child = child_class(child_dir, name, descr)
        self.__add(child)
        self._dispatch(ExpStructBoxEvent, ExpStructBoxEvent.MAKE_CHILD)
        return child

    def _destroy_child(self, num_or_name, confirm=True):
        self._update()
        child = self._get_child_by_num_or_name(num_or_name)
        child_dir = self._get_child_dir(child.num)
        if not confirm or util.response(f"ACHTUNG! Remove `{child}` and its `{child_dir}` dir with all its content?"):
            self.__remove(child)
            shutil.rmtree(child_dir)
            self._dispatch(ExpStructBoxEvent, ExpStructBoxEvent.DESTROY_CHIlD)
            return child
        return None

    def _children(self):
        self._update()
        return list(self.__num_to_child.values())

    def _nums(self):
        self._update()
        return list(self.__num_to_child.keys())

    def _names(self):
        self._update()
        return list(self.__name_to_child.keys())

    def _get_child_by_status(self, status_or_list):
        sl = status_or_list if type(status_or_list) is list else [status_or_list]
        for status in sl:
            for child in self._children():
                if child._status.status == status:
                    return child
        return None

    def _info(self):
        text = super()._info()
        for child in self._children():
            text += util.tab(f"\n\n{child._info()}")
        return text

    def _ExpStructEvent_listener(self, event: ExpStructEvent):
        self._update()
        if event.kind == ExpStructEvent.CHANGE_NAME_REQUESTED:
            event.respondent = self
            event.response = event.request not in self.__name_to_child

    def _ExpStructBoxEvent_listener(self, event: ExpStructBoxEvent): self._update()
