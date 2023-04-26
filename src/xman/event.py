class Event:
    pass


class UpdateEvent(Event):

    def __init__(self, exp, group=None):
        super().__init__()
        self.exp = exp
        self.group = group


class EventDispatcher:

    def __init__(self):
        self._listeners = {}
        self._destroyed = False

    def __check_destroyed(self):
        if self._destroyed:
            raise AssertionError(f"'{self}' was destroyed before!")

    def _add_listener(self, event_type, listener):
        self.__check_destroyed()
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    def _remove_listener(self, event_type, listener):
        self.__check_destroyed()
        listeners = self._listeners[event_type]
        if event_type in self._listeners and listener in listeners:
            listeners.remove(listener)
        else:
            raise ValueError(f"There's no listener `{listener}` with event_type `{event_type}`!")

    def _dispatch(self, event: Event):
        self.__check_destroyed()
        event_type = type(event)
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                listener(event)

    def _destroy(self):
        self.__check_destroyed()
        self._destroyed = True
        for event_type in list(self._listeners.keys()):
            listeners = self._listeners[event_type]
            for listener in listeners:
                listeners.remove(listener)
            del self._listeners[event_type]
        del self._listeners


