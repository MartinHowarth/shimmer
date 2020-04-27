"""Module defining windows."""

from dataclasses import dataclass, replace
from typing import Dict, Optional

from ..alignment import (
    LeftTop,
    CenterBottom,
    RightTop,
)
from ..components.box import Box, BoxDefinition, DynamicSizeBehaviourEnum
from ..components.box_layout import BoxColumn
from ..components.draggable_box import DragParentBox, DraggableBoxDefinition
from ..components.focus import make_focusable, VisualAndKeyboardFocusBox
from ..components.font import FontDefinition, Calibri
from ..components.mouse_box import (
    MouseClickEventCallable,
    MouseBox,
    MouseVoidBoxDefinition,
)
from ..data_structures import Color
from ..widgets.button import Button
from ..widgets.close_button import (
    CloseButton,
    CloseButtonDefinitionBase,
)
from ..widgets.text_box import TextBox, TextBoxDefinition


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

    # Text to display in the title bar of the window.
    title: Optional[str] = None
    title_font_definition: FontDefinition = Calibri

    # Height of the title bar. If None then it will match the height of the title font.
    # This is in addition to the the `height` of the window, which controls the height of the
    # window body.
    title_bar_height: Optional[int] = None

    # Space to leave between buttons in the title bar
    title_bar_button_spacing: int = 2
    title_bar_color: Color = Color(20, 120, 255)

    # Background color of the body of the window.
    background_color: Color = Color(20, 20, 20)

    # For dynamically sized windows (i.e. width, height = None, None) add this amount of space
    # between the children of the body and the edges of the window on all sides.
    padding: int = 15

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


class Window(MouseBox):
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

        self._title: Optional[TextBox] = self._create_title()
        self._title_boxes: Dict[str, Box] = {
            "close": self._create_close_button(),
            "drag": self._create_drag_zone(),
        }
        self._title_bar_background: Box = self._create_title_bar_background()
        self.focus_box: VisualAndKeyboardFocusBox = make_focusable(self)

        # Add the inner box, which is the main body of the window excluding the title bar.
        self.body = BoxColumn()
        self.add(self.body)

        self.arrange_children()

    @property
    def close_button(self) -> CloseButton:
        """Get the close button of this window."""
        return self._title_boxes["close"]

    @property
    def drag_box(self) -> DragParentBox:
        """Get the DraggableBox of this window."""
        return self._title_boxes["drag"]

    def make_focused(self):
        """Make this window the current focus target."""
        self.focus_box.take_focus()

    def arrange_children(self):
        self.close_button.align_anchor_with_other_anchor(
            self,
            RightTop,
            spacing=(
                -self.definition.title_bar_button_spacing,
                -self.definition.title_bar_button_spacing,
            ),
        )
        if self._title is not None:
            self._title.align_anchor_with_other_anchor(self, LeftTop, spacing=(10, 0))
        self._title_bar_background.align_anchor_with_other_anchor(self, LeftTop)
        self.drag_box.align_anchor_with_other_anchor(
            self, LeftTop,
        )
        self.body.align_anchor_with_other_anchor(
            self, CenterBottom, spacing=(0, self.definition.padding)
        )
        super(Window, self).arrange_children()

    def update_rect(self):
        """
        Update the cached rect definition.

        If the rect size changes, then `on_size_change` will be called.
        """
        if self.definition.is_dynamic_sized:
            # We don't use bounding_rect_of_children here because we are rearranging those
            # children in space at the same time which gets confusing - so hard coded calculation
            # for now at least.
            children_rect = self.body.rect.copy()
            children_rect.height += self.title_bar_height
            children_rect.height += 2 * self.definition.padding
            children_rect.width += 2 * self.definition.padding

            if self._title is not None:
                children_rect.width = max(
                    children_rect.width, self.minimum_title_bar_width
                )

            self._width = children_rect.width
            self._height = children_rect.height
        else:
            self._width = self.definition.width or 0
            self._height = self.definition.height or 0

        if self._width != self._rect.width or self._height != self._rect.height:
            self._rect.set_size((self._width, self._height))
            self.on_size_change()

    @property
    def minimum_title_bar_width(self) -> int:
        """
        Minimum width, in pixels, of the window title bar.

        This is determined by the length of the title text and any title bar buttons.
        """
        width = self.close_button.rect.width + self.definition.title_bar_button_spacing

        if self._title is not None:
            width += self._title.rect.width + self._title.x

        return width

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

    def _create_title(self) -> Optional[TextBox]:
        """Recreate the title."""
        if self.definition.title is None:
            return

        title_definition = TextBoxDefinition(
            text=self.definition.title, height=self.definition.title_bar_height,
        )

        title = TextBox(title_definition)
        self.add(title, no_resize=True)
        return title

    def _create_title_bar_background(self) -> Box:
        """Redefine the background color of the title bar."""
        title_background = Box(
            BoxDefinition(
                width=None,
                height=self.title_bar_height,
                background_color=self.definition.title_bar_color,
                dynamic_size_behaviour=DynamicSizeBehaviourEnum.match_parent,
            )
        )
        self.add(title_background, z=-1, no_resize=True)
        return title_background

    def _create_close_button(self) -> CloseButton:
        """Redefine the window close button."""
        definition = replace(
            CloseButtonDefinitionBase,
            width=self._title_bar_button_height,
            height=self._title_bar_button_height,
            on_release=self.definition.on_close,
        )
        close_button = CloseButton(definition)
        self.add(close_button, no_resize=True)
        return close_button

    def _create_drag_zone(self) -> DragParentBox:
        """
        Redefine the draggable area of the title bar.

        This creates a draggable area of the window covering the entire title bar to the left of
        the leftmost title bar button.
        """
        drag_box_definition = DraggableBoxDefinition(
            width=None,
            height=self.title_bar_height,
            dynamic_size_behaviour=DynamicSizeBehaviourEnum.match_parent,
        )
        drag_box = DragParentBox(drag_box_definition)
        # Add with z=-1 so the drag box is behind the title bar buttons.
        self.add(drag_box, no_resize=True, z=-1)
        return drag_box

    def add_child_to_body(self, child: Box) -> None:
        """
        Add a child to the body of the window.

        Children will be arranged vertically in the order they were added from bottom to top.

        For more precise control, replace the `body` with any other Box you want by removing the
        default body and adding your own.

        :param child: The child Box to add.
        """
        self.body.add(child)

    def close(self):
        """Close this window by simulating a click on the close button."""
        self.close_button.on_keyboard_select_release()
