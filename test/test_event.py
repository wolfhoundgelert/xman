from xman.struct import ExpStructEvent
from xman.event import Event, EventDispatcher


def test__dispatching():
    event = ExpStructEvent(None, ExpStructEvent.STATUS_CHANGED)
    dispatcher = EventDispatcher()

    def listener(e: Event):
        assert e == event

    dispatcher._add_listener(Event, listener)
    dispatcher._dispatch(event)
