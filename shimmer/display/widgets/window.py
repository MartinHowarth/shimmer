"""Module defining windows."""
import cocos

from typing import Dict, Optional

from ..primitives import create_rect
from ..data_structures import Color
from ..components.draggable_anchor import DraggableAnchor
from ..components.box import Box, ActiveBox
from ..components.mouse_box import MouseBox
from shimmer.display.widgets.close_button import CloseButton


class Window(ActiveBox):
    """
    A Window is a draggable, closeable Box with a title bar.

    It has an inner_box for containing children for displaying inside the window.
    """

    _title_bar_height: int = 20
    # Space to leave between buttons in the title bar
    _title_bar_button_spacing: int = 2
    _title_bar_color: Color = Color(20, 120, 255)
    _background_color: Color = Color(20, 20, 20)

    def __init__(self, rect: cocos.rect.Rect):
        """
        Create a Window.

        :param rect: Rect defining the entire window, including the title bar.
        """
        super(Window, self).__init__(rect)
        self.inner_box: Box = Box(self._inner_box_rect)
        self.title_boxes: Dict[str, Box] = {}
        self._title_bar_background: Optional[cocos.layer.ColorLayer] = None
        self._update_title_bar_background()
        self._update_background()
        self._update_close_button()
        self._update_drag_zone()

    @property
    def _inner_box_rect(self) -> cocos.rect.Rect:
        """Rect defining the window excluding the title bar."""
        return cocos.rect.Rect(
            0, 0, self.rect.width, self.rect.height - self._title_bar_height
        )

    @property
    def _title_bar_button_height(self):
        """Height of the title bar buttons, accounting for spacing."""
        return self._title_bar_height - (2 * self._title_bar_button_spacing)

    @property
    def _leftmost_title_bar_button_position(self) -> int:
        """Return the leftmost edge of the buttons in the title bar."""
        return min(
            [
                self.rect.width - box.x
                for box in self.title_boxes.values()
                if isinstance(box, MouseBox)
            ]
        )

    def _create_square_title_button_rect(self, x: int) -> cocos.rect.Rect:
        """
        Rect defining a square title bar button.

        :param x: X position of the button.
        :return: Rect defining a square title bar button.
        """
        edge_length = self._title_bar_button_height
        return cocos.rect.Rect(
            x,
            self.rect.height - self._title_bar_height + self._title_bar_button_spacing,
            edge_length,
            edge_length,
        )

    def _update_title_bar_background(self):
        """Redefine the background color of the title bar."""
        if self._title_bar_background is not None:
            self.remove(self._title_bar_background)

        self._title_bar_background = create_rect(
            self.rect.width, self._title_bar_height, self._title_bar_color
        )
        self._title_bar_background.position = (
            0,
            self.rect.height - self._title_bar_height,
        )
        self.add(self._title_bar_background, z=-1)

    def _update_background(self):
        """Redefine the background color of the window body."""
        if self._background is not None:
            self.remove(self._background)

        self._background = create_rect(
            self.rect.width,
            self.rect.height - self._title_bar_height,
            self._background_color,
        )
        self._background.position = (0, 0)
        self.add(self._background, z=-1)

    def _update_close_button(self):
        """Redefine the window close button."""
        close_button_rect = self._create_square_title_button_rect(
            self.rect.width
            - (self._title_bar_button_height + self._title_bar_button_spacing)
        )

        self._update_title_bar_box("close", CloseButton(close_button_rect))

    def _update_drag_zone(self):
        """
        Redefine the draggable area of the title bar.

        This creates a draggable area of the window covering the entire title bar to the left of
        the leftmost title bar button.
        """
        drag_anchor_rect = cocos.rect.Rect(
            0,
            self.rect.height - self._title_bar_height,
            self.rect.width - self._leftmost_title_bar_button_position,
            self._title_bar_height,
        )

        self._update_title_bar_box("drag", DraggableAnchor(drag_anchor_rect))

    def _update_title_bar_box(self, name: str, box: Box):
        """
        Create or re-create a title bar Box known by the given name.

        :param name: Internal identifier of the Box.
        :param box: New Box node to place in the title bar.
        """
        if name in self.title_boxes.keys():
            self.remove(self.title_boxes[name])

        self.add(box)
        self.title_boxes[name] = box
