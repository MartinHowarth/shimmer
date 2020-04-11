"""Box that can be dragged, changing the position of it's parent as well."""

from dataclasses import dataclass, replace
from typing import Optional, Callable, Sequence

import cocos
from shimmer.alignment import CenterCenter
from shimmer.components.box import Box, BoxDefinition
from shimmer.components.mouse_box import (
    MouseBox,
    MouseBoxDefinition,
    EVENT_HANDLED,
)


@dataclass(frozen=True)
class SnapBoxDefinition(BoxDefinition):
    """
    Definition of a SnapBox.

    :param can_receive: Callback to test whether a DraggableBox should be allowed to snap
        to this SnapBox. Return True if yes, otherwise return False if not allowed.
    :param on_receive: Callback called when a DraggableBox snaps onto this SnapBox.
    :param on_release: Callback called when a DraggableBox snaps off this SnapBox.
    """

    can_receive: Optional[Callable[["DraggableBox"], bool]] = None
    on_receive: Optional[Callable[["DraggableBox"], None]] = None
    on_release: Optional[Callable[["DraggableBox"], None]] = None


class SnapBox(Box):
    """
    A Box that a DraggableBox can snap to.

    This causes the DraggableBox to be centered on this SnapBox when dragged over it.

    SnapBoxes are single occupancy - multiple DraggableBoxes cannot snap to the same SnapBox.
    """

    def __init__(self, definition: SnapBoxDefinition):
        """Create a new SnapBox."""
        super(SnapBox, self).__init__(definition)
        self.definition: SnapBoxDefinition = self.definition
        self.occupant: Optional[Box] = None

    @property
    def is_occupied(self) -> bool:
        """Return True if this SnapBox is currently occupied. Otherwise False."""
        return self.occupant is not None

    def can_receive(self, other: "DraggableBox") -> bool:
        """
        Return True if the given DraggableBox is allowed to snap to this SnapBox.

        :param other: The DraggableBox to be tested.
        """
        if self.is_occupied:
            return False
        elif self.definition.can_receive is not None:
            return self.definition.can_receive(other)
        return True

    def receive(self, other: "DraggableBox") -> None:
        """
        Called when a DraggableBox is snapped to this SnapBox.

        Calls the "on_receive" callback in the definition, if given.

        :param other: The DraggableBox that has snapped to this SnapBox.
        """
        self.occupant = other
        if self.definition.on_receive is not None:
            self.definition.on_receive(other)

    def release(self, other: "DraggableBox") -> None:
        """
        Called when a DraggableBox is no longer snapped to this SnapBox.

        Calls the "on_release" callback in the definition, if given.

        :param other: The DraggableBox that is not longer snapped to this SnapBox.
        """
        self.occupant = None
        if self.definition.on_release is not None:
            self.definition.on_release(other)


@dataclass(frozen=True)
class DraggableBoxDefinition(MouseBoxDefinition):
    """
    Definition of a draggable box.

    MouseBox actions will be overwritten when initialising the DraggableBox

    :param snap_boxes: List of SnapBoxes which the draggable anchor will snap to.
        Snapping means when the anchor is dragged over a snap box, their centers will be aligned.
    :param must_be_snapped: If True then this DraggableBox must always be snapped to a SnapBox.
        If it is dragged off a SnapBox and not onto another one then it will return to its
        previous position.
        If True, then "snap_boxes" must be given.
        Note: This is not enforced on creation; only on subsequent drags.
              Use DraggableBox.snap_to(snap_box) to set up snap behaviour on creation.
    """

    snap_boxes: Optional[Sequence[SnapBox]] = None
    must_be_snapped: bool = False

    def __post_init__(self):
        """Perform validation."""
        if self.must_be_snapped:
            if self.snap_boxes is None or len(self.snap_boxes) == 0:
                raise ValueError(
                    f"`snap_boxes` must be given if `requires_snap_box` is True. {self.snap_boxes=}"
                )


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
        self._currently_snapped_to: Optional[SnapBox] = None
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

    def stop_dragging(
        self, box: "MouseBox", x: int, y: int, buttons: int, modifiers: int,
    ) -> bool:
        """
        Set this box as no longer being dragged.

        If this DraggableBox is defined with `must_be_snapped` then move it back to the current
        SnapBox if needed.
        """
        if self.definition.must_be_snapped and self._currently_snapped_to is not None:
            self._snap_drag_record = cocos.draw.Vector2(0, 0)
            self._align_with_snap_box(self._currently_snapped_to)
        return super(DraggableBox, self).stop_dragging(box, x, y, buttons, modifiers)

    def handle_drag(
        self, box: Box, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
    ) -> Optional[bool]:
        """
        While the mouse is pressed on the area, keep updating the position.

        If snap_boxes are defined, then this DraggableBox will center its parent (and therefore
        itself) to one of the SnapBoxes if they overlap and other conditions are met as defined
        in the SnapBoxDefinition.
        """
        if self.definition.snap_boxes is None:
            self.parent.position += cocos.draw.Vector2(dx, dy)
        else:
            self._snap_drag_record += (dx, dy)
            self.parent.position += self._snap_drag_record
            # Move the parent by the snap record so we can test if we still intersect a snap point
            # It will get moved back it we still intersect the current snap point.
            # If we don't intersect with any snap point, then we will have just moved the parent
            # by the correct displacement anyway.
            for snap_box in self.definition.snap_boxes:
                if (
                    snap_box is self._currently_snapped_to or snap_box.can_receive(self)
                ) and self.world_rect.intersects(snap_box.world_rect):
                    self.snap_to(snap_box)
                    break
            else:
                # If no longer intersecting any valid snap boxes, then stop being snapped
                self._snap_drag_record = cocos.draw.Vector2(0, 0)
                self.unsnap_if_snapped()

        return EVENT_HANDLED

    def snap_to(self, snap_box: SnapBox) -> None:
        """
        Call to snap this DraggableBox to the given SnapBox.

        This aligns the center of this box with the snap box by moving the parent of this box.

        :param snap_box: The SnapBox to snap to.
        """
        # Only release/receive to snap box if it has changed.
        if self._currently_snapped_to is not snap_box:
            if self._currently_snapped_to is not None:
                self._currently_snapped_to.release(self)

            self._currently_snapped_to = snap_box
            snap_box.receive(self)

        # Always align with the target box, regardless of whether it has changed or not.
        self._align_with_snap_box(snap_box)

    def unsnap_if_snapped(self) -> None:
        """
        Call to unsnap from the current SnapBox, if there is a current SnapBox.

        If this DraggableBox is defined as `must_be_snapped` then this has no effect.

        Does not move this DraggableBox, but notifies the current SnapBox (if there is one)
        that this box is no longer snapped to it.
        """
        # Don't unsnap if this DraggableBox must always be snapped - this essentially
        # reserves its current snap target for it to return to if the drag ends before
        # it reaches another snap target.
        if not self.definition.must_be_snapped:
            if self._currently_snapped_to is not None:
                self._currently_snapped_to.release(self)
            self._currently_snapped_to = None

    def _align_with_snap_box(self, snap_box: SnapBox) -> None:
        """Align the parent of this DraggableBox with the given snap box."""
        self.logger.debug(f"Aligning with snap box {snap_box}.")
        alignment_required = self.vector_between_anchors(
            snap_box, CenterCenter, CenterCenter
        )
        self.parent.position += alignment_required
        if self._currently_snapped_to is not None:
            # Set the drag record to be the inverse motion. This allows the user to drag on/off
            # the snap point repeatedly right at the edge of the snap box.
            self._snap_drag_record = -alignment_required
            self._currently_snapped_to = snap_box
