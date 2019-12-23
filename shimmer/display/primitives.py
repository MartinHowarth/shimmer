"""Collection of basic graphical constructs."""

import cocos
import logging

from abc import abstractmethod
from typing import Any, Tuple

from shimmer.log_utils import log_exceptions
from shimmer.display.data_structures import Color

log = logging.getLogger(__name__)


def create_color_rect(width: int, height: int, color: Color) -> cocos.layer.ColorLayer:
    """Create a colored rectangle."""
    return cocos.layer.ColorLayer(*color.as_tuple_alpha(), width=width, height=height)


class UpdatingNode(cocos.cocosnode.CocosNode):
    """
    A Node which updates regularly.

    Only performs an update if `self.dirty` is set to True.

    `dirty` can either be set by an third party; or this node will mark itself as dirty
    if the value returned by `self._current_indicator_value()` changes.
    """

    def __init__(self):
        """Create a new UpdatingNode."""
        super(UpdatingNode, self).__init__()
        self.schedule(self.update)
        self.dirty = False

        # Set to globally unique value so first update always happens.
        self.__last_indicator_value: Any = object()

    def _check_if_dirty(self):
        """Mark this node as dirty if the indicator value has changed."""
        indicator_value = self._current_indicator_value()
        if self.__last_indicator_value != indicator_value:
            self.__last_indicator_value = indicator_value
            self.dirty = True

    def _current_indicator_value(self) -> Any:
        """
        Trigger self-updating by changing the value that this returns.

        Implementing this is optional, if not implemented then this object
        will never self-update.
        """
        pass

    @abstractmethod
    def _update(self, dt: float) -> None:
        """Should be overridden to define what this node does in an update."""
        pass

    @log_exceptions(log)
    def update(self, dt: float) -> None:
        """Called on every frame to determine if this node needs to update itself."""
        # Only update if the value has changed to save on drawing performance.
        self._check_if_dirty()
        if self.dirty:
            self.dirty = False
            self._update(dt)


Point2d = Tuple[int, int]
