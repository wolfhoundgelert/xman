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

    def _add_listener(self, event_type, listener):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    def _remove_listener(self, event_type, listener):
        if event_type in self._listeners and listener in self._listeners[event_type]:
            self._listeners[event_type].remove(listener)
        else:
            raise ValueError(f"There's no listener `{listener}` with event_type `{event_type}`!")

    def _dispatch(self, event: Event):
        event_type = type(event)
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                listener(event)
