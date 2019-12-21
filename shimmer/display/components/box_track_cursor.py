"""Definition of a Box that tracks the cursor."""

from typing import Optional

import cocos

from shimmer.display.components.box import ActiveBox
from shimmer.display.primitives import Point2d


class BoxTrackCursor(ActiveBox):
    """A Box that tracks the cursor."""

    def __init__(self, rect: cocos.rect.Rect, offset: Optional[Point2d] = None):
        """
        Create a BoxTrackCursor.

        :param rect: Rect area of the Box.
        :param offset: x, y offset from the cursor to the bottom-left corner of the pop up.
        """
        self._original_pos = rect.x, rect.y
        super(BoxTrackCursor, self).__init__(rect)
        if offset is None:
            offset = 0, 0
        self.offset = offset

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        """
        Cocos director callback when the mouse is moved.

        Updates the position of this Box to the cursor position.

        Does not capture the event, so it may be handled by other entities as well.
        """
        coord = cocos.director.director.get_virtual_coordinates(x, y)
        # Position is relative to the parent, so need the mouse coordinates translated into the
        # local space of the parent to determine the correct relative position of this Box.
        self.position = self.parent.point_to_local(coord) + self.offset
