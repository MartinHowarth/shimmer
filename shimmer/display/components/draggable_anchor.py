"""Box that can be dragged, changing the position of it's parent as well."""

import cocos

from typing import Optional
from pyglet.event import EVENT_UNHANDLED, EVENT_HANDLED

from shimmer.display.components.box import ActiveBox

# TODO refactor to be based on MouseBox
class DraggableAnchor(ActiveBox):
    """Box that can be dragged, changing the position of it's parent as well."""

    def __init__(
        self, rect: Optional[cocos.rect.Rect] = None,
    ):
        """Creates a new DraggableAnchor."""
        super(DraggableAnchor, self).__init__(rect)

        # Used to record whether we're currently dragging this Box.
        # This is needed because if the user drags too fast then we can't just rely on
        # a drag event being inside the box area still.
        self._currently_dragging: bool = False

    def on_mouse_press(self, x, y, buttons, modifiers):
        """If the user clicks within the area, start dragging the anchor and its parent."""
        if self.parent is None:
            return EVENT_UNHANDLED

        coord = cocos.director.director.get_virtual_coordinates(x, y)
        if self.contains_coord(*coord):
            self._currently_dragging = True
            return EVENT_HANDLED

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """While the mouse is pressed on the area, keep updating the position."""
        if not self._currently_dragging:
            return EVENT_UNHANDLED

        new_parent_pos_x = self.parent.position[0] + dx
        new_parent_pos_y = self.parent.position[1] + dy

        self.parent.position = new_parent_pos_x, new_parent_pos_y
        return EVENT_HANDLED

    def on_mouse_release(self, x, y, buttons, modifiers):
        """On mouse release, stop dragging this Box."""
        self._currently_dragging = False
