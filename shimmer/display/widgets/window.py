"""Module defining windows."""

from dataclasses import dataclass, replace
from typing import Dict, Optional, Union, Tuple

import cocos
from ..alignment import (
    PositionalAnchor,
    CenterCenter,
    CenterTop,
)
from ..components.box import Box, BoxDefinition, ActiveBox
from ..components.draggable_anchor import DraggableAnchor
from ..components.focus import make_focusable
from ..components.font import FontDefinition, Calibri
from ..components.mouse_box import (
    MouseClickEventCallable,
    MouseBox,
    MouseVoidBoxDefinition,
)
from ..data_structures import Color
from ..primitives import create_color_rect
from ..widgets.button import Button
from ..widgets.close_button import (
    CloseButton,
    CloseButtonDefinitionBase,
)
from ..widgets.text_box import TextBox, TextBoxDefinition


@dataclass(frozen=True)
class WindowDefinition(BoxDefinition):
    """
    Definition of the visual style of a Window.

    Inherits from MouseVoidBoxDefinition so that the default window swallows all mouse events
    that happen within it. Other components can be added into the window that can receive
    those events first. This prevents users clicking on a window and something underneath
    the window receiving the event accidentally.

    The `height` parameter is set on init to be the sum of the `body_height` and the
    `title_bar_height`.
    """

    width: int = 200

    # Height of the window body, excluding the title bar.
    body_height: int = 200

    title: Optional[str] = None
    title_font_definition: FontDefinition = Calibri

    # Height of the title bar. If None then it will match the height of the title font.
    title_bar_height: Optional[int] = None

    # Space to leave between buttons in the title bar
    title_bar_button_spacing: int = 2
    title_bar_color: Color = Color(20, 120, 255)
    background_color: Color = Color(20, 20, 20)

    # Callback to call when the window is closed using the close button.
    on_close: Optional[MouseClickEventCallable] = None

    def get_title_bar_height(self) -> int:
        """
        Height of the title bar.

        This is the defined height `title_bar_height` if given,
        otherwise the height of the title font.
        """
        if self.title_bar_height is not None:
            return self.title_bar_height
        return self.title_font_definition.height

    def __post_init__(self):
        """
        Initialise the `height` of the window.

        This sets height to the sum of the body and title bar heights.
        """
        # Have to use this __setattr__ workaround because the dataclass is frozen.
        object.__setattr__(
            self, "height", self.body_height + self.get_title_bar_height()
        )


class Window(ActiveBox):
    """
    A Window is a draggable, closeable Box with a title bar.

    It has an inner_box for containing children for displaying inside the window.

    All nodes added to the window are placed above this VoidBox so they receive the mouse events
    first.
    """

    def __init__(self, definition: WindowDefinition):
        """
        Create a Window.

        :param definition: Definition of the Window style.
        """
        self.definition: WindowDefinition = definition
        self.title_bar_height = self.definition.get_title_bar_height()

        super(Window, self).__init__(definition)

        self._title: Optional[cocos.text.Label] = None
        self._title_boxes: Dict[str, Box] = {}
        self._title_bar_background: Optional[cocos.layer.ColorLayer] = None
        self._update_title()
        self._update_title_bar_background()
        self.update_background()
        self._update_close_button()
        self._update_drag_zone()
        self.focus_box = make_focusable(self)

        # Add the inner box, which is the main body of the window excluding the title bar.
        self.body: Box = Box(
            BoxDefinition(
                width=self.definition.width, height=self.definition.body_height,
            )
        )
        self.add(self.body)
        self.add(
            MouseBox(
                MouseVoidBoxDefinition(
                    width=self.definition.width, height=self.definition.height,
                )
            ),
            z=-10000,
        )

    @property
    def _title_bar_button_height(self):
        """Height of the title bar buttons, accounting for spacing."""
        return self.title_bar_height - (2 * self.definition.title_bar_button_spacing)

    @property
    def _leftmost_title_bar_button_position(self) -> int:
        """Return the leftmost edge of the buttons in the title bar."""
        return min(
            [
                self.rect.width - box.x
                for box in self._title_boxes.values()
                if isinstance(box, Button)
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
            self.rect.height
            - self.title_bar_height
            + self.definition.title_bar_button_spacing,
            edge_length,
            edge_length,
        )

    def _update_title(self):
        """Recreate the title."""
        if self._title is not None:
            self.remove(self._title)

        if self.definition.title is None:
            return

        title_definition = TextBoxDefinition(
            text=self.definition.title,
            height=self.definition.title_bar_height,
            width=self.definition.width,
        )

        self._title = TextBox(title_definition)
        self.add(self._title)
        self._title.align_anchor_with_other_anchor(self, CenterTop)
        self._title.x = 10

    def _update_title_bar_background(self):
        """Redefine the background color of the title bar."""
        if self._title_bar_background is not None:
            self.remove(self._title_bar_background)

        self._title_bar_background = create_color_rect(
            self.rect.width, self.title_bar_height, self.definition.title_bar_color,
        )
        self._title_bar_background.position = (
            0,
            self.rect.height - self.title_bar_height,
        )
        self.add(self._title_bar_background, z=-1)

    def _update_close_button(self):
        """Redefine the window close button."""
        close_button_rect = self._create_square_title_button_rect(
            self.rect.width
            - (self._title_bar_button_height + self.definition.title_bar_button_spacing)
        )
        definition = replace(
            CloseButtonDefinitionBase,
            width=close_button_rect.width,
            height=close_button_rect.height,
            on_release=self.definition.on_close,
        )
        close_button = CloseButton(definition)
        close_button.position = close_button_rect.position
        self._update_title_bar_box("close", close_button)

    @property
    def close_button(self) -> CloseButton:
        """Get the close button of this window."""
        return self._title_boxes["close"]

    def _update_drag_zone(self):
        """
        Redefine the draggable area of the title bar.

        This creates a draggable area of the window covering the entire title bar to the left of
        the leftmost title bar button.
        """
        drag_anchor_definition = BoxDefinition(
            width=self.rect.width - self._leftmost_title_bar_button_position,
            height=self.title_bar_height,
        )
        self._update_title_bar_box("drag", DraggableAnchor(drag_anchor_definition))
        self._title_boxes["drag"].position = 0, self.rect.height - self.title_bar_height

    def _update_title_bar_box(self, name: str, box: Box) -> None:
        """
        Create or re-create a title bar Box known by the given name.

        :param name: Internal identifier of the Box.
        :param box: New Box node to place in the title bar.
        """
        if name in self._title_boxes.keys():
            self.remove(self._title_boxes[name])

        self.add(box)
        self._title_boxes[name] = box

    def add_child_to_body(
        self,
        child: Box,
        body_anchor: PositionalAnchor = CenterCenter,
        child_anchor: Optional[PositionalAnchor] = None,
        spacing: Union[int, Tuple[int, int], cocos.draw.Point2] = 0,
    ) -> None:
        """
        Add a child to the body of the window aligned to the edges or center of the window.

        See Box.align_anchor_with_other_anchor for fuller documentation.

        If you want finer control over spacing, then you should set positions and add children
        directly to the `body`.

        :param child: The child Box to add.
        :param body_anchor: The anchor point of the window body to align to.
            Defaults to CenterCenter.
        :param child_anchor: The anchor point of the child to align.
            Defaults to match `body_anchor`.
        :param spacing: Pixels to leave between the anchors.
        """
        child.align_anchor_with_other_anchor(
            self.body, body_anchor, child_anchor, spacing
        )
        self.body.add(child)

    def close(self):
        """Close this window by simulating a click on the close button."""
        self.close_button.on_keyboard_select_release()
