"""
Definition of the Box primitive.

A Box is a CocosNode that defines an area.
"""

import cocos

from dataclasses import dataclass, replace
from typing import Optional, Union, Type, Iterable, Generator

from ..data_structures import Color, HorizontalAlignment, VerticalAlignment, ZIndexEnum
from ..primitives import create_color_rect


@dataclass(frozen=True)
class BoxDefinition:
    """Common definition to all Boxes."""

    width: int = 0
    height: int = 0

    background_color: Optional[Color] = None

    def as_rect(self) -> cocos.rect.Rect:
        """Return a Rect of the size defined by this BoxDefinition."""
        return cocos.rect.Rect(0, 0, self.width, self.height)


class Box(cocos.cocosnode.CocosNode):
    """A CocosNode that has a defined rectangular area."""

    definition_type: Type[BoxDefinition] = BoxDefinition

    def __init__(self, definition: Optional[BoxDefinition] = None):
        """Creates a new Box."""
        super(Box, self).__init__()
        if definition is None:
            definition = self.definition_type()

        self.definition = definition
        self._rect = self.definition.as_rect()
        self._background: Optional[cocos.layer.ColorLayer] = None
        self._update_background()

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
        self.definition = replace(self.definition, width=rect.width, height=rect.height)
        self._rect = self.definition.as_rect()
        self._update_background()

    def set_size(self, width: int, height: int) -> None:
        """Update the size of this Box without changing position."""
        self._update_rect(cocos.rect.Rect(*self.position, width, height))

    def get_z_value(self) -> int:
        """
        Get the z value of this Box in its parents children list.

        Raises ValueError if this child is not a child of parent (should never happen).
        """
        if self.parent is None:
            raise AttributeError(f"{self} has no parent.")

        for z, child in self.parent.children:
            if child is self:
                return z
        raise ValueError(f"{self} is not a child of its parent.")

    def set_z_value(self, z: Union[int, ZIndexEnum]) -> None:
        """
        Set the z value of this box in its parents list of children.

        The z value controls ordering of drawing, and ordering of event handling.

        Higher z means:
          - Drawn on top of lower z nodes.
          - Receives events first (and therefore may stop them propagating to lower z nodes)
                Note: This happens because in ActiveBox we push own events before children do.

        Warning: This removes and re-adds this node to the parent, so `on_exit` and `on_enter`
            are called.
            For ActiveBoxes this will remove and re-add it to the event stack. So if the z value
            is changed during an event callback, the event may skip children of THIS node.
            This can be worked around by consuming the event when changing the Z value, and
            re-dispatching it (see FocusBox for an example of this).

        :param z: Int or member of ZIndexEnum to set the z value to.
        """
        if z is ZIndexEnum.top:
            # Children are in z order from lowest to highest, so highest z is the last one.
            # Children are stored as the tuple (z, node)
            if self.parent.children[-1][1] is self:
                # If this box is already at the top, then do nothing.
                return
            z = self.parent.children[-1][0] + 1
        elif z is ZIndexEnum.bottom:
            # Children are in z order from lowest to highest, so lowest z is the first one.
            # Children are stored as the tuple (z, node)
            if self.parent.children[0][1] is self:
                # If this box is already at the top, then do nothing.
                return
            z = self.parent.children[0][0] - 1

        # Remove and re-add to insert this node in the child list correctly, and perform
        # `on_exit` and `on_enter` to make sure that the node is in the correct place in the
        # event stack.
        self.parent.remove(self)
        self.parent.add(self, z=z)

    def _update_background(self):
        """Set the background color of this Box."""
        # Remove the old background
        if self._background is not None:
            self.remove(self._background)

        # Don't create a new background if the color is None
        # (this allows removal of the background color)
        if self.definition.background_color is None:
            return

        self._background = create_color_rect(
            self.definition.width,
            self.definition.height,
            self.definition.background_color,
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

    def get_family_tree(self) -> Generator["Box", None, None]:
        """
        Generate all children, grandchildren (etc) of this Box that are also Boxes.

        Also yields this Box.
        """
        yield self
        for child in self.get_children():
            if isinstance(child, Box):
                yield from child.get_family_tree()

    def bounding_rect_of_children(self) -> cocos.rect.Rect:
        """
        Return the rect that contains all the children Boxes of this Box.

        This recursively finds all children of this boxes children as well.
        """
        return bounding_rect_of_boxes(self.get_family_tree())


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


def bounding_rect_of_boxes(boxes: Iterable[Box]) -> cocos.rect.Rect:
    """
    Return the minimal rect needed to cover all the given boxes.

    This is calculated in the coordinate space of the parent of the boxes.
    If the boxes do not share a common parent then the resulting rect may be odd.
    """
    lefts, rights, tops, bottoms = zip(
        *(
            (box.x, box.x + box.definition.width, box.y + box.definition.height, box.y)
            for box in boxes
        )
    )

    left = min(lefts)
    bottom = min(bottoms)
    right = max(rights)
    top = max(tops)

    x = min(left, right)
    y = min(bottom, top)
    width = max(left, right) - x
    height = max(bottom, top) - y

    return cocos.rect.Rect(x, y, width, height)
