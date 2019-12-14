from dataclasses import dataclass
from typing import Optional

import cocos

from shimmer.display.components.mouse_box import (
    MouseBoxDefinition,
    MouseBox,
    bitwise_contains,
)
from shimmer.display.data_structures import Color
from shimmer.display.primitives import create_rect


@dataclass
class VisibleButtonDefinition(MouseBoxDefinition):
    """A Button definition with visual elements."""

    text: Optional[str] = None
    base_color: Color = Color(0, 111, 255)
    depressed_color: Optional[Color] = None
    hover_color: Optional[Color] = None


class VisibleButton(MouseBox):
    """
    A Button that has visual elements.

    Changes color when hovered over or clicked on.
    """

    definition: VisibleButtonDefinition

    def __init__(
        self,
        definition: VisibleButtonDefinition,
        rect: Optional[cocos.rect.Rect] = None,
    ):
        """Creates a new VisibleButton."""
        super(VisibleButton, self).__init__(definition, rect)
        self.label: Optional[cocos.text.Label] = None
        self.color_rect: cocos.layer.ColorLayer = None
        self.update_label()
        self.update_color_layer()

    @property
    def rect(self) -> cocos.rect.Rect:
        return self._rect

    @rect.setter
    def rect(self, value: cocos.rect.Rect):
        self._rect = value
        self.update_label()
        self.update_color_layer()

    def update_label(self):
        """Recreate the button label."""
        if self.definition.text is None:
            self.label = None
            return

        if self.label is not None:
            self.remove(self.label)

        self.label = cocos.text.Label(
            self.definition.text,
            font_name="calibri",
            font_size=16,
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )
        self.label.position = self.rect.width / 2, self.rect.height / 2
        self.add(self.label)

    def update_color_layer(self):
        """Recreate the button color layer."""
        if self.color_rect is not None:
            self.remove(self.color_rect)

        # Include the `or 1` to override cocos default behaviour to make the
        # layer the size of the entire window.
        self.color_rect = create_rect(
            self.rect.width or 1, self.rect.height or 1, self.definition.base_color
        )
        self.add(self.color_rect, z=-1)

    def _should_handle_mouse_press(self, buttons) -> bool:
        """Whether this button should handle mouse press events."""
        return (
            self.definition.on_press is not None
            # Also handle if on_release is defined so we can record which mouse button was used.
            or self.definition.on_release is not None
            or self.definition.depressed_color is not None
        )

    def _should_handle_mouse_release(self, buttons) -> bool:
        """Whether this button should handle mouse release events."""
        return (
            # Also handle if on_press is defined so we can record which mouse button was used.
            self.definition.on_press is not None
            or self.definition.on_release is not None
            or self.definition.depressed_color is not None
        ) and bitwise_contains(self._currently_pressed, buttons)

    def _should_handle_mouse_hover(self) -> bool:
        """Whether this button should handle mouse hover and unhover events."""
        return (
            self.definition.on_hover is not None
            or self.definition.on_unhover is not None
            or self.definition.hover_color is not None
        )

    def _on_press(self, x, y, buttons, modifiers):
        """Change the button color and call the on_press callback."""
        super(VisibleButton, self)._on_press(x, y, buttons, modifiers)
        if self.definition.depressed_color is not None:
            self.color_rect.color = self.definition.depressed_color.as_tuple()
            # self.color_rect.opacity = self.definition.depressed_color.a

    def _on_release(self, x, y, buttons, modifiers):
        """Change the button color and call the on_release callback."""
        super(VisibleButton, self)._on_release(x, y, buttons, modifiers)
        if self._currently_hovered:
            if self.definition.hover_color is not None:
                self.color_rect.color = self.definition.hover_color.as_tuple()
                # self.color_rect.opacity = self.definition.hover_color.a
        else:
            self.color_rect.color = self.definition.base_color.as_tuple()
            # self.color_rect.opacity = self.definition.base_color.a

    def _on_hover(self, x, y, dx, dy):
        """Change the button color and call the on_hover callback."""
        super(VisibleButton, self)._on_hover(x, y, dx, dy)
        if self.definition.hover_color is not None:
            self.color_rect.color = self.definition.hover_color.as_tuple()
            # self.color_rect.opacity = self.definition.hover_color.a

    def _on_unhover(self, x, y, dx, dy):
        """Change the button color and call the on_unhover callback."""
        super(VisibleButton, self)._on_unhover(x, y, dx, dy)
        if self.definition.hover_color is not None:
            self.color_rect.color = self.definition.base_color.as_tuple()
            # self.color_rect.opacity = self.definition.base_color.a
