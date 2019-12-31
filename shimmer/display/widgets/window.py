"""Module defining windows."""

import cocos

from dataclasses import dataclass, replace
from typing import Dict, Optional

from ..primitives import create_color_rect
from ..data_structures import (
    Color,
    LabelDefinition,
    VerticalAlignment,
    VerticalTextAlignment,
    HorizontalAlignment,
    FontDefinition,
    Calibri,
)
from ..components.box import Box, BoxDefinition
from ..components.draggable_anchor import DraggableAnchor
from ..components.focus import make_focusable
from ..components.mouse_box import (
    MouseBox,
    MouseClickEventCallable,
    MouseVoidBoxDefinition,
)
from shimmer.display.widgets.button import Button
from shimmer.display.widgets.close_button import (
    CloseButton,
    CloseButtonDefinitionBase,
)


@dataclass(frozen=True)
class WindowDefinition(MouseVoidBoxDefinition):
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


class Window(MouseBox):
    """
    A Window is a draggable, closeable Box with a title bar.

    It has an inner_box for containing children for displaying inside the window.

    The window itself is a MouseVoidBox which prevents all mouse events propagating further.
    This means that windows can be appear above other nodes without the user accidentally
    interacting with the node underneath.

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
        self.title_boxes: Dict[str, Box] = {}
        self._title_bar_background: Optional[cocos.layer.ColorLayer] = None
        self._update_title()
        self._update_title_bar_background()
        self._update_background()
        self._update_close_button()
        self._update_drag_zone()
        self.focus_box = make_focusable(self)

        # Add the inner box, which is the main body of the window excluding the title bar.
        self.inner_box: Box = Box(
            BoxDefinition(
                width=self.definition.width, height=self.definition.body_height,
            )
        )
        self.add(self.inner_box)

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
                for box in self.title_boxes.values()
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

    def _create_title(self):
        """Create the title node. Does not add it to the window."""
        if self.definition.title is None:
            return

        title_definition = LabelDefinition(
            text=self.definition.title,
            # NB: this uses the defined title bar height, rather than the dynamic property on
            # this class.
            height=self.definition.title_bar_height,
            width=self.definition.width,
            anchor_y=VerticalTextAlignment.center,
        )

        self._title = cocos.text.Label(**title_definition.to_pyglet_label_kwargs())
        self._title.position = (
            10,
            self.definition.height - (self.title_bar_height / 2),
        )

    def _update_title(self):
        """Recreate the title."""
        if self._title is not None and self._title in self:
            self.remove(self._title)

        if self.definition.title is None:
            return

        self._create_title()
        self.add(self._title)

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

    def _update_background(self):
        """Redefine the background color of the window body."""
        if self._background is not None:
            self.remove(self._background)

        self._background = create_color_rect(
            self.rect.width,
            self.rect.height - self.title_bar_height,
            self.definition.background_color,
        )
        self.add(self._background, z=-1)

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
        return self.title_boxes["close"]

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
        self.title_boxes["drag"].position = 0, self.rect.height - self.title_bar_height

    def _update_title_bar_box(self, name: str, box: Box) -> None:
        """
        Create or re-create a title bar Box known by the given name.

        :param name: Internal identifier of the Box.
        :param box: New Box node to place in the title bar.
        """
        if name in self.title_boxes.keys():
            self.remove(self.title_boxes[name])

        self.add(box)
        self.title_boxes[name] = box

    def add_child_to_body(
        self,
        child: Box,
        align_x: HorizontalAlignment = HorizontalAlignment.center,
        align_y: VerticalAlignment = VerticalAlignment.center,
        margin_x: int = 0,
        margin_y: int = 0,
    ) -> None:
        """
        Add a child to the body of the window aligned to the edges or center of the window.

        This provides 9 easy positions to place Boxes inside this window.
        For example:
          - Center = HorizontalAlignment.center, VerticalAlignment.center
          - Top-middle = HorizontalAlignment.center, VerticalAlignment.top
          - ...

        Default is to place the child in the centre of the window.

        If you want finer control over spacing, then you should set positions and add children
        directly to the `inner_box`.

        :param child: The child Box to add.
        :param align_x: X alignment of the child.
        :param align_y: Y alignment of the child.
        :param margin_x: Space to leave between edge of window and the box.
            Has no effect for "center" alignment.
        :param margin_y: Space to leave between edge of window and the box.
            Has no effect for "center" alignment.
        """
        child.set_position_in_alignment_with(self.inner_box, align_x, align_y)
        if margin_x:
            if align_x == HorizontalAlignment.left:
                child.x += margin_x
            elif align_x == HorizontalAlignment.right:
                child.x -= margin_x
        if margin_y:
            if align_y == VerticalAlignment.bottom:
                child.y += margin_y
            elif align_y == VerticalAlignment.top:
                child.y -= margin_y
        self.inner_box.add(child)

    def close(self):
        """Close this window by simulating a click on the close button."""
        self.close_button.on_keyboard_select_release()
