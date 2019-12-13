"""
Definition of the Box primitive.

A Box is a CocosNode that defines an area.
"""

import cocos

from typing import Optional


class Box(cocos.cocosnode.CocosNode):
    """A CocosNode that has a defined rectangular area."""

    def __init__(self, rect: Optional[cocos.rect.Rect] = None):
        """
        Creates a new Box.

        :param rect: Definition of the rectangle that this Box encompasses.
        """
        super(Box, self).__init__()
        self._rect = rect if rect is not None else cocos.rect.Rect(0, 0, 0, 0)

    def contains_coord(self, x: int, y: int) -> bool:
        """Returns whether the point (x,y) is inside the box."""
        p = self.point_to_local((x, y))
        return self.rect.contains(p.x, p.y)

    @property
    def rect(self) -> cocos.rect.Rect:
        return self._rect

    @rect.setter
    def rect(self, value: cocos.rect.Rect):
        self._rect = value
        self.position = self._rect.x, self._rect.y


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
        cocos.director.director.window.push_handlers(self)
        super(ActiveBox, self).on_exit()
