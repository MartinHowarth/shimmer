"""Module defining a close button that removes its parent Node from the scene when clicked."""

import cocos

from typing import Optional, Callable

from shimmer.display.data_structures import Color
from shimmer.display.widgets.button import VisibleButtonDefinition, VisibleButton


def make_close_button_definition(
    on_release: Optional[Callable],
) -> VisibleButtonDefinition:
    """
    Create a close button definition that calls the given callback when clicked.

    :param on_release: Action to take when clicked.
    :return: Definition of the button.
    """
    return VisibleButtonDefinition(
        text="X",
        base_color=Color(200, 0, 127),
        hover_color=Color(255, 0, 127),
        on_release=on_release,
    )


class CloseButton(VisibleButton):
    """Standard close button that removes its parent CocosNode when clicked."""

    def __init__(
        self, rect: Optional[cocos.rect.Rect] = None,
    ):
        """See Button for argument definitions."""
        defn = make_close_button_definition(self._kill_parent)
        super(CloseButton, self).__init__(defn, rect)

    def _kill_parent(self, *_, **__):
        """Kill the parent of this button, which will kill all its children too."""
        self.parent.kill()
