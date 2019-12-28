"""Definition of a Box that tracks the cursor."""

import cocos

from dataclasses import dataclass
from typing import Optional

from shimmer.display.components.box import ActiveBox, BoxDefinition
from shimmer.display.primitives import Point2d


@dataclass(frozen=True)
class BoxTrackCursorDefinition(BoxDefinition):
    """
    Definition of a Box that tracks the cursor.

    :param offset: (x, y) offset from the cursor position to set the Box position to.
    """

    offset: Point2d = (0, 0)


class BoxTrackCursor(ActiveBox):
    """A Box that tracks the cursor."""

    definition_type = BoxTrackCursorDefinition

    def __init__(self, definition: Optional[BoxTrackCursorDefinition] = None):
        """Create a BoxTrackCursor."""
        super(BoxTrackCursor, self).__init__(definition)
        self.definition: BoxTrackCursorDefinition = self.definition

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        """
        Cocos director callback when the mouse is moved.

        Updates the position of this Box to the cursor position.

        Does not capture the event, so it may be handled by other entities as well.
        """
        coord = cocos.director.director.get_virtual_coordinates(x, y)
        # Position is relative to the parent, so need the mouse coordinates translated into the
        # local space of the parent to determine the correct relative position of this Box.
        self.position = self.parent.point_to_local(coord) + self.definition.offset
