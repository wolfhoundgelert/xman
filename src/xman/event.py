from inspect import signature
from typing import Type

from .error import WasDestroyedXManError
from . import util


class Event:  # Generic event, can't be used - other `xman` events should inherit from this one.

    def __init__(self, target, kind):
        self.target = target
        self.kind = kind
        util.check_has_value_in_class_public_constants(kind, self)

    def __str__(self):
        cls = self.__class__
        cls_str = cls.__module__ + '.' + cls.__name__
        params = signature(cls).parameters
        params_list = [f"{param.name}=`{getattr(self, param.name)}`" for param in params.values()
                       if param.name != 'self']
        params_str = f"({', '.join(params_list)})"
        return f"{cls_str}{params_str}"


class EventDispatcher:

    def __init__(self):
        self.__event_type_to_listeners = {}
        self.__destroyed = False

    def __check_destroyed(self):
        if self.__destroyed:
            raise WasDestroyedXManError(f"'{self}' was destroyed before!")

    def _has_listener(self, event_type, listener):
        self.__check_destroyed()
        return event_type in self.__event_type_to_listeners and \
            listener in self.__event_type_to_listeners[event_type]

    def _has_listeners(self, event_type):
        self.__check_destroyed()
        return event_type in self.__event_type_to_listeners

    def _add_listener(self, event_type, listener):
        self.__check_destroyed()
        if event_type not in self.__event_type_to_listeners:
            self.__event_type_to_listeners[event_type] = []
        listeners = self.__event_type_to_listeners[event_type]
        if listener not in listeners:
            listeners.append(listener)

    def _remove_listener(self, event_type, listener):
        self.__check_destroyed()
        if event_type in self.__event_type_to_listeners:
            listeners = self.__event_type_to_listeners[event_type]
            if listener in listeners:
                listeners.remove(listener)
            if not len(listeners):
                del self.__event_type_to_listeners[event_type]

    def _dispatch(self, event_type: Type[Event], *args, **kwargs) -> Event:
        self.__check_destroyed()
        event = None
        if event_type in self.__event_type_to_listeners:
            event = event_type(self, *args, **kwargs)
            for listener in self.__event_type_to_listeners[event_type]:
                listener(event)
        return event

    def _destroy(self):
        self.__check_destroyed()
        self.__destroyed = True
        for event_type in list(self.__event_type_to_listeners.keys()):
            listeners = self.__event_type_to_listeners[event_type]
            listeners.clear()
            del self.__event_type_to_listeners[event_type]
        self.__event_type_to_listeners = None
