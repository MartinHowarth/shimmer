"""
Definition of the Box primitive.

A Box is a CocosNode that defines an area.
"""

import cocos

from typing import Optional
from ..data_structures import Color
from ..primitives import create_rect


class Box(cocos.cocosnode.CocosNode):
    """A CocosNode that has a defined rectangular area."""

    # If defined, the box will be filled with this color.
    _background_color: Optional[Color] = None

    def __init__(self, rect: Optional[cocos.rect.Rect] = None):
        """
        Creates a new Box.

        :param rect: Definition of the rectangle that this Box encompasses.
        """
        super(Box, self).__init__()
        self._rect = rect if rect is not None else cocos.rect.Rect(0, 0, 0, 0)
        self._update_rect(self._rect)
        self._background: Optional[cocos.layer.ColorLayer] = None
        self._update_background()

    def contains_coord(self, x: int, y: int) -> bool:
        """Returns whether the point (x,y) is inside the box."""
        p = self.point_to_local((x, y))
        return self.rect.contains(p.x, p.y)

    @property
    def rect(self) -> cocos.rect.Rect:
        return self._rect

    @rect.setter
    def rect(self, value: cocos.rect.Rect):
        """
        Intercept setting of the rect to re-position this Box onto the given rect.

        :param value: Rect to set this Box to.
        """
        self._rect = value
        self._update_rect(value)

    def _update_rect(self, rect: cocos.rect.Rect):
        """Update the position of this Box to the given box."""
        self.position = rect.x, rect.y
        self._rect.x = 0
        self._rect.y = 0

    @property
    def background_color(self) -> Optional[Color]:
        return self._background_color

    @background_color.setter
    def background_color(self, value: Optional[Color]):
        self._background_color = value
        self._update_background()

    def _update_background(self):
        """Redefine the background color of the pop up."""
        if self._background_color is None:
            return

        if self._background is not None:
            self.remove(self._background)

        self._background = create_rect(
            self.rect.width, self.rect.height, self._background_color,
        )
        self._background.position = (0, 0)
        self.add(self._background, z=-1)


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
