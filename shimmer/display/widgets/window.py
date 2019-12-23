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
)
from ..components.draggable_anchor import DraggableAnchor
from ..components.box import Box, ActiveBox
from ..components.mouse_box import MouseBox, MouseClickEventCallable
from shimmer.display.widgets.close_button import (
    CloseButton,
    CloseButtonDefinitionBase,
)


@dataclass(frozen=True)
class WindowDefinition:
    """Definition of the visual style of a Window."""

    width: int = 200
    # Height does not include the title bar, i.e. this is the height of the window body.
    height: int = 180

    title: Optional[str] = None

    # Height of the title bar. If None then it will match the height of the title.
    # If None, then a title must be given.
    title_bar_height: Optional[int] = 20

    # Space to leave between buttons in the title bar
    title_bar_button_spacing: int = 2
    title_bar_color: Color = Color(20, 120, 255)
    background_color: Color = Color(20, 20, 20)

    # Callback to call when the window is closed using the close button.
    on_close: Optional[MouseClickEventCallable] = None

    def __post_init__(self):
        """Validation checks for inter-dependent fields."""
        if self.title is None and self.title_bar_height is None:
            raise ValueError(
                "Cannot have both `title` and `title_bar_height` set to None."
            )


class Window(ActiveBox):
    """
    A Window is a draggable, closeable Box with a title bar.

    It has an inner_box for containing children for displaying inside the window.
    """

    def __init__(self, definition: WindowDefinition):
        """
        Create a Window.

        :param definition: Definition of the Window style.
        """
        self.definition: WindowDefinition = definition
        # Create the title first so we can determine dynamically set title bar height.
        self._title: Optional[cocos.text.Label] = None
        self._create_title()
        # Set the rect of this window to include the title bar.
        super(Window, self).__init__(
            cocos.rect.Rect(
                0, 0, definition.width, definition.height + self.title_bar_height
            )
        )
        self.title_boxes: Dict[str, Box] = {}
        self._title_bar_background: Optional[cocos.layer.ColorLayer] = None
        self._update_title()  # Re-update title to make sure it's laid out correctly.
        self._update_title_bar_background()
        self._update_background()
        self._update_close_button()
        self._update_drag_zone()

        # Add the inner box, which is the main body of the window excluding the title bar.
        self.inner_box: Box = Box(self._inner_box_rect)
        self.add(self.inner_box)

    @property
    def title_bar_height(self) -> int:
        """
        Height of the title bar.

        This is the defined height `title_bar_height` if given,
        otherwise the height of the title.
        """
        if self.definition.title_bar_height is not None:
            return self.definition.title_bar_height
        elif self._title is not None:
            return self._title.element.content_height
        raise ValueError(
            "Title bar height is not known yet - initialise the window first."
        )

    @property
    def _inner_box_rect(self) -> cocos.rect.Rect:
        """Rect defining the window excluding the title bar."""
        return cocos.rect.Rect(
            0, 0, self.rect.width, self.rect.height - self.title_bar_height
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
            self.definition.height + (self.title_bar_height / 2),
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
        close_button.rect = close_button_rect
        self._update_title_bar_box("close", close_button)

    def _update_drag_zone(self):
        """
        Redefine the draggable area of the title bar.

        This creates a draggable area of the window covering the entire title bar to the left of
        the leftmost title bar button.
        """
        drag_anchor_rect = cocos.rect.Rect(
            0,
            self.rect.height - self.title_bar_height,
            self.rect.width - self._leftmost_title_bar_button_position,
            self.title_bar_height,
        )

        self._update_title_bar_box("drag", DraggableAnchor(drag_anchor_rect))

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
        """
        child.set_position_in_alignment_with(self.inner_box, align_x, align_y)
        self.inner_box.add(child)
