"""Module of alignment definitions."""

from dataclasses import dataclass
from enum import Enum

import cocos


class HorizontalAlignment(Enum):
    """Enum of possible values for horizontal alignment in pyglet."""

    left = "left"
    right = "right"
    center = "center"


class VerticalAlignment(Enum):
    """Enum of possible values for vertical alignment in pyglet."""

    bottom = "bottom"
    center = "center"
    top = "top"


class VerticalTextAlignment(Enum):
    """Enum of possible values for vertical alignment of text in pyglet."""

    bottom = "bottom"
    center = "center"
    top = "top"
    # Baseline is the bottom of the first line of text, as opposed to `bottom` which is
    # the bottom of the pyglet text layout.
    baseline = "baseline"


class ZIndexEnum(Enum):
    """Indicators of where in the stack of cocos children to add a child."""

    top = "top"
    bottom = "bottom"


@dataclass(frozen=True)
class PositionalAnchor:
    """Pair of alignments that define a relative anchor point in 2D space."""

    horizontal: HorizontalAlignment
    vertical: VerticalAlignment

    @property
    def x(self) -> HorizontalAlignment:
        """Synonym for `self.horizontal`."""
        return self.horizontal

    @property
    def y(self) -> VerticalAlignment:
        """Synonym for `self.vertical`."""
        return self.vertical

    def get_coord_in_rect(self, width: int, height: int) -> cocos.draw.Point2:
        """
        Get the (x, y) coordinate of this anchor in the given rect.

        :param width: The width of the rect to consider.
        :param height: The height of the rect to consider.
        :return: cocos.draw.Point2 of the anchor position.
        """
        x, y = 0.0, 0.0

        if self.horizontal == HorizontalAlignment.left:
            x = 0
        elif self.horizontal == HorizontalAlignment.center:
            x = width / 2
        elif self.horizontal == HorizontalAlignment.right:
            x = width

        if self.vertical == VerticalAlignment.bottom:
            y = 0
        elif self.vertical == VerticalAlignment.center:
            y = height / 2
        elif self.vertical == VerticalAlignment.top:
            y = height

        return cocos.draw.Point2(x, y)


# Define the 9 basic anchor points of a rectangle.
LeftTop = PositionalAnchor(HorizontalAlignment.left, VerticalAlignment.top)
LeftCenter = PositionalAnchor(HorizontalAlignment.left, VerticalAlignment.center)
LeftBottom = PositionalAnchor(HorizontalAlignment.left, VerticalAlignment.bottom)
CenterTop = PositionalAnchor(HorizontalAlignment.center, VerticalAlignment.top)
CenterCenter = PositionalAnchor(HorizontalAlignment.center, VerticalAlignment.center)
CenterBottom = PositionalAnchor(HorizontalAlignment.center, VerticalAlignment.bottom)
RightTop = PositionalAnchor(HorizontalAlignment.right, VerticalAlignment.top)
RightCenter = PositionalAnchor(HorizontalAlignment.right, VerticalAlignment.center)
RightBottom = PositionalAnchor(HorizontalAlignment.right, VerticalAlignment.bottom)
