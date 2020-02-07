"""Box that can be dragged, changing the position of it's parent as well."""

import logging
from dataclasses import dataclass, replace
from typing import Optional, Iterable

import cocos
from shimmer.display.alignment import CenterCenter
from shimmer.display.components.box import Box
from shimmer.display.components.mouse_box import (
    MouseBox,
    MouseBoxDefinition,
    EVENT_HANDLED,
)

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class DraggableBoxDefinition(MouseBoxDefinition):
    """
    Definition of a draggable box.

    MouseBox actions will be overwritten when initialising the DraggableBox

    :param snap_boxes: List of Boxes which the draggable anchor will snap to.
        Snapping means when the anchor is dragged over a snap box, their centers will be aligned.
    """

    snap_boxes: Optional[Iterable[Box]] = None


class DraggableBox(MouseBox):
    """Box that can be dragged, changing the position of it's parent as well."""

    def __init__(self, definition: DraggableBoxDefinition):
        """
        Creates a new DraggableBox.

        :param definition: DraggableBoxDefinition defining the shape of the draggable box.
        """
        defn = replace(
            definition,
            on_press=self.start_dragging,
            on_release=self.stop_dragging,
            on_drag=self.handle_drag,
        )
        super(DraggableBox, self).__init__(defn)
        self.definition: DraggableBoxDefinition = self.definition
        self._currently_snapped: bool = False
        self._snap_drag_record: cocos.draw.Vector2 = cocos.draw.Vector2(0, 0)

    def _should_handle_mouse_press(self, buttons: int) -> bool:
        """Should only handle events if this box is attached to something."""
        return self.parent is not None

    def _should_handle_mouse_release(self, buttons: int) -> bool:
        """Should only handle events if this box is attached to something."""
        return self.parent is not None

    def _should_handle_mouse_drag(self) -> bool:
        """Should only handle drag is this box currently is being dragged."""
        return self._currently_dragging

    def start_dragging(
        self, box: "MouseBox", x: int, y: int, buttons: int, modifiers: int,
    ) -> bool:
        """Set this box as being dragged, and reset previous drag knowledge."""
        self._snap_drag_record = cocos.draw.Vector2(0, 0)
        return super(DraggableBox, self).start_dragging(box, x, y, buttons, modifiers)

    def handle_drag(
        self, box: Box, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
    ) -> Optional[bool]:
        """While the mouse is pressed on the area, keep updating the position."""
        self._snap_drag_record += (dx, dy)
        self.parent.position += self._snap_drag_record

        if self.definition.snap_boxes is not None:
            # Move the parent by the snap record so we can test if we still intersect a snap point
            # It will get moved back it we still intersect the current snap point.
            # If we don't intersect with any snap point, then we will have just moved the parent
            # by the correct displacement anyway.
            for snap_box in self.definition.snap_boxes:
                if self.world_rect.intersects(snap_box.world_rect):
                    self._align_with_snap_box(snap_box)
                    break
            else:
                # If no longer intersecting any snap boxes, then stop being snapped
                self._snap_drag_record = cocos.draw.Vector2(0, 0)
                self._currently_snapped = False

        return EVENT_HANDLED

    def _align_with_snap_box(self, snap_box: Box) -> None:
        """Align the parent of this DraggableBox with the given snap box."""
        log.debug(f"Aligning {self} with snap box {snap_box}.")
        alignment_required = self.vector_between_anchors(
            snap_box, CenterCenter, CenterCenter
        )
        self.parent.position += alignment_required
        if not self._currently_snapped:
            # Set the drag record to be the inverse motion. This allows the user to drag on/off
            # the snap point repeatedly right at the edge of the snap box.
            self._snap_drag_record = -alignment_required
            self._currently_snapped = True
