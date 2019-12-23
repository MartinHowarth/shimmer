"""
Definition of the Box primitive.

A Box is a CocosNode that defines an area.
"""

import cocos

from typing import Optional
from ..data_structures import Color, HorizontalAlignment, VerticalAlignment
from ..primitives import create_color_rect


class Box(cocos.cocosnode.CocosNode):
    """A CocosNode that has a defined rectangular area."""

    def __init__(self, rect: Optional[cocos.rect.Rect] = None):
        """
        Creates a new Box.

        :param rect: Definition of the rectangle that this Box encompasses.
        """
        super(Box, self).__init__()
        # And init the rect to a minimal size to guarantee existence.
        self._rect = rect if rect is not None else cocos.rect.Rect(0, 0, 0, 0)
        self._background_color: Optional[Color] = None
        self._background: Optional[cocos.layer.ColorLayer] = None
        self._update_rect(self._rect)

    def contains_coord(self, x: int, y: int) -> bool:
        """Returns whether the point (x,y) is inside the box."""
        p = self.point_to_local((x, y))
        return self.rect.contains(p.x, p.y)

    @property
    def rect(self) -> cocos.rect.Rect:
        """Return the rect that this box encompasses."""
        return self._rect

    @rect.setter
    def rect(self, value: cocos.rect.Rect) -> None:
        """
        Intercept setting of the rect to re-position this Box onto the given rect.

        If you only want to change the size of this Box without changing its position, use
        `self.set_size(width, height)` instead.

        :param value: Rect to set this Box to.
        """
        self._update_rect(value)
        self._update_background()

    @property
    def world_rect(self) -> cocos.rect.Rect:
        """Get the rect for this Box in world coordinate space."""
        # Boxes set their rect position to be 0, 0 (the Box's position is set to the rect coords
        # instead).
        return cocos.rect.Rect(
            *self.point_to_world((0, 0)), self.rect.width, self.rect.height
        )

    def _update_rect(self, rect: cocos.rect.Rect) -> None:
        """Update the position and size of this Box to the given rect."""
        self.position = rect.x, rect.y
        rect.x = 0
        rect.y = 0
        self._rect = rect

    def set_size(self, width: int, height: int) -> None:
        """Update the size of this Box without changing position."""
        self._update_rect(cocos.rect.Rect(*self.position, width, height))
        self._update_background()

    @property
    def background_color(self) -> Optional[Color]:
        """Get the background color of this Box."""
        return self._background_color

    @background_color.setter
    def background_color(self, value: Optional[Color]) -> None:
        """Set the background color of this Box."""
        self._background_color = value
        self._update_background()

    def _update_background(self):
        """Set the background color of this Box."""
        # Remove the old background
        if self._background is not None:
            self.remove(self._background)

        # Don't create a new background if the color is None
        # (this allows removal of the background color)
        if self._background_color is None:
            return

        self._background = create_color_rect(
            self.rect.width, self.rect.height, self._background_color,
        )
        self._background.position = (0, 0)
        self.add(self._background, z=-1)

    def set_transform_anchor(
        self,
        anchor_x: Optional[HorizontalAlignment] = None,
        anchor_y: Optional[VerticalAlignment] = None,
    ) -> None:
        """
        Set the cocos transform anchor to the given alignments.

        :param anchor_x: Enum member defining the X anchor position to set.
            If None, then horizontal anchor is left unchanged.
        :param anchor_y: Enum member defining the Y anchor position to set.
            If None, then vertical anchor is left unchanged.
        """
        if anchor_x is None:
            pass
        elif anchor_x == HorizontalAlignment.left:
            self.anchor_x = 0
        elif anchor_x == HorizontalAlignment.center:
            self.anchor_x = self.rect.width / 2
        elif anchor_x == HorizontalAlignment.right:
            self.anchor_x = self.rect.width

        if anchor_y is None:
            pass
        elif anchor_y == VerticalAlignment.bottom:
            self.anchor_y = 0
        elif anchor_y == VerticalAlignment.center:
            self.anchor_y = self.rect.height / 2
        elif anchor_y == VerticalAlignment.top:
            self.anchor_y = self.rect.height

    def set_center_as_transform_anchor(self):
        """Set the cocos transform anchor to the center point."""
        self.set_transform_anchor(HorizontalAlignment.center, VerticalAlignment.center)

    def set_bottom_left_as_transform_anchor(self):
        """Set the cocos transform anchor to the bottom left. This is the default on creation."""
        self.set_transform_anchor(HorizontalAlignment.left, VerticalAlignment.bottom)

    def set_position_in_alignment_with(
        self,
        other: "Box",
        align_x: Optional[HorizontalAlignment] = None,
        align_y: Optional[VerticalAlignment] = None,
    ) -> None:
        """
        Set the position of this Box to be aligned with the given point of the other Box.

        This provides 9 easy positions to arrange Boxes inside this box.
        For example:
          - Center = HorizontalAlignment.center, VerticalAlignment.center
          - Top-middle = HorizontalAlignment.center, VerticalAlignment.top
          - ...

        :param other: The Box to align this one with.
        :param align_x: The horizontal alignment to set.
            If None, X position is left unchanged.
        :param align_y: The vertical alignment to set.
            If None, Y position is left unchanged.
        """
        if align_x is None:
            pass
        elif align_x == HorizontalAlignment.left:
            self.x = 0
        elif align_x == HorizontalAlignment.center:
            self.x = (other.rect.width / 2) - (self.rect.width / 2)
        elif align_x == HorizontalAlignment.right:
            self.x = other.rect.width - self.rect.width

        if align_y is None:
            pass
        elif align_y == VerticalAlignment.bottom:
            self.y = 0
        elif align_y == VerticalAlignment.center:
            self.y = (other.rect.height / 2) - (self.rect.height / 2)
        elif align_y == VerticalAlignment.top:
            self.y = other.rect.height - self.rect.height


class ActiveBox(Box):
    """A Box that adds itself to the cocos director event handlers when entering the scene."""

    def on_enter(self):
        """Called every time just before the node enters the stage."""
        # Deliberately push handlers for this node before calling for sub nodes. This causes
        # handlers for children to be inserted higher in the stack than their parents,
        # resulting in them getting higher priority on handling events.
        # This makes sense because children are generally smaller / drawn on top of parents.
        cocos.director.director.window.push_handlers(self)
        super(ActiveBox, self).on_enter()

    def on_exit(self):
        """Called every time just before the node exits the stage."""
        cocos.director.director.window.remove_handlers(self)
        super(ActiveBox, self).on_exit()
