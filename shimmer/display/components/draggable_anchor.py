import cocos

from typing import Optional
from pyglet.event import EVENT_UNHANDLED, EVENT_HANDLED

from shimmer.display.components.box import ActiveBox


class DraggableAnchor(ActiveBox):
    def __init__(
        self, rect: Optional[cocos.rect.Rect] = None,
    ):
        """Creates a new Button."""
        super(DraggableAnchor, self).__init__(rect)
        self._currently_dragging: bool = False

    def on_mouse_press(self, x, y, buttons, modifiers):
        if self.parent is None:
            return EVENT_UNHANDLED

        coord = cocos.director.director.get_virtual_coordinates(x, y)
        if self.contains_coord(*coord):
            self._currently_dragging = True
            return EVENT_HANDLED

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self._currently_dragging:
            return EVENT_UNHANDLED

        new_parent_pos_x = self.parent.position[0] + dx
        new_parent_pos_y = self.parent.position[1] + dy

        self.parent.position = new_parent_pos_x, new_parent_pos_y
        return EVENT_HANDLED

    def on_mouse_release(self, x, y, buttons, modifiers):
        self._currently_dragging = False
