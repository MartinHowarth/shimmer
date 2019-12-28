"""Mock versions of the graphical dependencies of cocos."""

import cocos

from typing import Any, List, Tuple, Dict


class MockWindow:
    """A Mock pyglet window."""

    def __init__(self, width: int = 640, height: int = 480):
        """Create a new MockWindow."""
        self.width = width
        self.height = height
        self.received_events: List[Tuple[str, Tuple, Dict]] = []

    def push_handlers(self, *_, **__):
        """Ignore pushing of handlers to the window."""

    def remove_handlers(self, *_, **__):
        """Ignore removing of handlers to the window."""

    def dispatch_event(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Record events that are dispatched."""
        self.received_events.append((event, args, kwargs))


class MockDirector(cocos.director.Director):
    """A Mock of the cocos Director."""

    def set_alpha_blending(self, on=True):
        """Ignore alpha blending."""
