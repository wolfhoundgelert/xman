import os
import sys

from xman.struct import ExpStructEvent

xman_path = os.path.abspath(os.path.join('src'))
if xman_path not in sys.path:
    sys.path.insert(0, xman_path)

from xman.event import Event, EventDispatcher


def test__dispatching():
    event = ExpStructEvent(None, ExpStructEvent.STATUS_CHANGED)
    dispatcher = EventDispatcher()

    def listener(e: Event):
        assert e == event

    dispatcher._add_listener(Event, listener)
    dispatcher._dispatch(event)



