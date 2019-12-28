"""Box that can be dragged, changing the position of it's parent as well."""

from shimmer.display.components.box import BoxDefinition
from shimmer.display.components.mouse_box import MouseBox, MouseBoxDefinition


class DraggableAnchor(MouseBox):
    """Box that can be dragged, changing the position of it's parent as well."""

    def __init__(self, definition: BoxDefinition):
        """
        Creates a new DraggableAnchor.

        :param definition: BoxDefinition defining the shape of the draggable anchor.
        """
        defn = MouseBoxDefinition(
            width=definition.width,
            height=definition.height,
            on_press=self.start_dragging,
            on_release=self.stop_dragging,
            on_drag=self.handle_drag,
        )
        super(DraggableAnchor, self).__init__(defn)

    def _should_handle_mouse_press(self, buttons: int) -> bool:
        """Should only handle events if this anchor is attached to something."""
        return self.parent is not None

    def _should_handle_mouse_release(self, buttons: int) -> bool:
        """Should only handle events if this anchor is attached to something."""
        return self.parent is not None

    def _should_handle_mouse_drag(self) -> bool:
        """Should only handle drag is this anchor currently is being dragged."""
        return self._currently_dragging

    def handle_drag(self, *_, dx=0, dy=0, **__):
        """While the mouse is pressed on the area, keep updating the position."""
        new_parent_pos_x = self.parent.position[0] + dx
        new_parent_pos_y = self.parent.position[1] + dy

        self.parent.position = new_parent_pos_x, new_parent_pos_y
