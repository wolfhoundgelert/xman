import os
import sys


xman_path = os.path.abspath(os.path.join('src'))
if xman_path not in sys.path:
    sys.path.insert(0, xman_path)

from xman.event import Event, EventDispatcher


def test__dispatching():
    event = Event(None)
    dispatcher = EventDispatcher()

    def listener(e: Event):
        assert e == event

    dispatcher._add_listener(Event, listener)
    dispatcher._dispatch(event)



