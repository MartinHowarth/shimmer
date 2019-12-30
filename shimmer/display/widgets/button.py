"""
A visible, clickable button.

Changes color when interacted with (clicked. on hover) and calls the defined methods.
"""

from dataclasses import dataclass
from typing import Optional

import cocos

from shimmer.display.components.mouse_box import (
    MouseBoxDefinition,
    MouseBox,
)
from shimmer.display.keyboard import (
    KeyboardActionDefinition,
    KeyMap,
    KeyboardHandler,
)
from shimmer.display.helpers import bitwise_contains
from shimmer.display.data_structures import Color, PassiveBlue, ActiveBlue, MutedBlue
from shimmer.display.primitives import create_color_rect


@dataclass(frozen=True)
class ButtonDefinition(MouseBoxDefinition):
    """A Button definition with visual elements."""

    text: Optional[str] = None
    base_color: Color = PassiveBlue
    depressed_color: Optional[Color] = MutedBlue
    hover_color: Optional[Color] = ActiveBlue

    # Automatically match the button size to the text size.
    dynamic_size: bool = False

    keyboard_shortcut: Optional[str] = None

    @property
    def formatted_text(self) -> Optional[str]:
        """
        Get the formatted text for this Button.

        When used in a RichLabel, underlines the keyboard shortcut if present in the text.
        """
        if (
            self.text is not None
            and self.keyboard_shortcut is not None
            and self.keyboard_shortcut in self.text
            and len(self.text) > 1
        ):
            # If the keyboard_shortcut appears in the text, and it's not the only character
            # then underline it.
            # This uses pyglets special in-built text formatting engine.
            # https://pyglet.readthedocs.io/en/stable/programming_guide/text.html#attributed-text
            index = self.text.index(self.keyboard_shortcut)
            underline_color = (255, 255, 255, 255)
            return "".join(
                (
                    self.text[:index],
                    f"{{underline {underline_color}}}"
                    f"{self.keyboard_shortcut}"
                    f"{{underline False}}",
                    self.text[index + 1 :],
                )
            )
        return self.text


class Button(MouseBox):
    """
    A Button that has visual elements.

    Changes color when hovered over or clicked on.
    """

    definition: ButtonDefinition

    def __init__(self, definition: ButtonDefinition):
        """
        Create a new Button.

        :param definition: Definition of the button.
        """
        super(Button, self).__init__(definition)
        self.label: Optional[cocos.text.Label] = None
        self.color_rect: cocos.layer.ColorLayer = None
        self.keyboard_handler: Optional[KeyboardHandler] = None
        self.update_label()
        self.update_color_layer()
        self.update_keyboard_handler()

    @property
    def rect(self) -> cocos.rect.Rect:
        """Get the rect defining the shape of this button."""
        return self._rect

    @rect.setter
    def rect(self, value: cocos.rect.Rect) -> None:
        """Set the rect defining the shape of this button and redraw the button."""
        self._update_rect(value)
        self.update_color_layer()
        self.update_label()

    def update_label(self):
        """Recreate the button label and update color layer as needed."""
        if self.label is not None:
            self.remove(self.label)

        if self.definition.text is None:
            self.label = None
            return

        self.label = cocos.text.RichLabel(
            self.definition.formatted_text,
            font_name="calibri",
            font_size=16,
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )
        # Set size dynamically if either defined width or height are None.
        if self.definition.dynamic_size:
            new_width = self.label.element.content_width
            new_height = self.label.element.content_height
            self.set_size(new_width, new_height)
            self.update_color_layer()

        self.label.position = self.rect.width / 2, self.rect.height / 2
        self.add(self.label)

    def update_color_layer(self):
        """Recreate the button color layer."""
        if self.color_rect is not None:
            self.remove(self.color_rect)

        # Include the `or 1` to override cocos default behaviour to make the
        # layer the size of the entire window.
        self.color_rect = create_color_rect(
            self.rect.width or 1, self.rect.height or 1, self.definition.base_color
        )
        self.add(self.color_rect, z=-1)

    def _should_handle_mouse_press(self, buttons: int) -> bool:
        """Whether this button should handle mouse press events."""
        return (
            self.definition.on_press is not None
            # Also handle if on_release is defined so we can record which mouse button was used.
            or self.definition.on_release is not None
            or self.definition.depressed_color is not None
        )

    def _should_handle_mouse_release(self, buttons: int) -> bool:
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

    def _on_press(self, x: int, y: int, buttons: int, modifiers: int) -> Optional[bool]:
        """Change the button color and call the on_press callback."""
        result = super(Button, self)._on_press(x, y, buttons, modifiers)
        if self.definition.depressed_color is not None:
            self.color_rect.color = self.definition.depressed_color.as_tuple()
            # self.color_rect.opacity = self.definition.depressed_color.a
        return result

    def _on_release(
        self, x: int, y: int, buttons: int, modifiers: int
    ) -> Optional[bool]:
        """Change the button color and call the on_release callback."""
        result = super(Button, self)._on_release(x, y, buttons, modifiers)
        if self._currently_hovered:
            if self.definition.hover_color is not None:
                self.color_rect.color = self.definition.hover_color.as_tuple()
                # self.color_rect.opacity = self.definition.hover_color.a
        else:
            self.color_rect.color = self.definition.base_color.as_tuple()
            # self.color_rect.opacity = self.definition.base_color.a
        return result

    def _on_hover(self, x: int, y: int, dx: int, dy: int) -> Optional[bool]:
        """Change the button color and call the on_hover callback."""
        result = super(Button, self)._on_hover(x, y, dx, dy)
        if self.definition.hover_color is not None:
            self.color_rect.color = self.definition.hover_color.as_tuple()
            # self.color_rect.opacity = self.definition.hover_color.a
        return result

    def _on_unhover(self, x: int, y: int, dx: int, dy: int) -> Optional[bool]:
        """Change the button color and call the on_unhover callback."""
        result = super(Button, self)._on_unhover(x, y, dx, dy)
        if self.definition.hover_color is not None:
            self.color_rect.color = self.definition.base_color.as_tuple()
            # self.color_rect.opacity = self.definition.base_color.a
        return result

    def on_keyboard_hover(self) -> Optional[bool]:
        """Called when the keyboard is used to navigate onto this button."""
        return self._on_hover(0, 0, 0, 0)

    def on_keyboard_unhover(self) -> Optional[bool]:
        """Called when the keyboard is used to navigate off this button."""
        return self._on_unhover(0, 0, 0, 0)

    def on_keyboard_select_press(self) -> Optional[bool]:
        """Called when the keyboard is used to press this button."""
        return self._on_press(0, 0, 0, 0)

    def on_keyboard_select_release(self) -> Optional[bool]:
        """Called when the keyboard is used to release this button."""
        return self._on_release(0, 0, 0, 0)

    def update_keyboard_handler(self):
        """
        Recreate the keyboard handler for this Button.

        Listens for keyboard presses for the configured keyboard_shortcut and
        activates on_press and on_release for this button on each key press.
        """
        self.keyboard_handler = None

        if self.definition.keyboard_shortcut is None:
            return

        keymap = KeyMap()
        keyboard_action = KeyboardActionDefinition(
            chords=[
                self.definition.keyboard_shortcut.upper(),
                self.definition.keyboard_shortcut.lower(),
            ],
            on_press=self.on_keyboard_select_press,
            on_release=self.on_keyboard_select_release,
        )
        keymap.add_keyboard_action(keyboard_action)
        self.keyboard_handler = KeyboardHandler(keymap)
        self.add(self.keyboard_handler)


class ToggleButton(Button):
    """A button that toggles on and off."""

    def __init__(self, definition: ButtonDefinition):
        """
        Create a new ToggleButton.

        :param definition: Definition of the button.
        """
        super(ToggleButton, self).__init__(definition)
        self._is_toggled: bool = False

    @property
    def is_toggled(self) -> bool:
        """Whether this button is currently toggled on."""
        return self._is_toggled

    @is_toggled.setter
    def is_toggled(self, value: bool) -> None:
        """
        Set the toggled state of this button.

        Calls the on_press / on_release as appropriate.
        """
        if self._is_toggled != value:
            # If requested state is different to current state, then toggle this button.
            self._on_press(0, 0, 0, 0)
        # Otherwise no action needed to toggle the button.

    def _on_press(self, x: int, y: int, buttons: int, modifiers: int) -> None:
        """
        Called when the Box is clicked by the user.

        Alternatively calls the `on_press` and `on_release` callback from the definition on each
        press.
        """
        self._is_toggled = not self._is_toggled
        if not self._is_toggled:
            super(ToggleButton, self)._on_release(x, y, buttons, modifiers)
        else:
            super(ToggleButton, self)._on_press(x, y, buttons, modifiers)

    def _should_handle_mouse_release(self, buttons: int) -> bool:
        """
        Toggle buttons do no react to mouse release events.

        Super of `on_release` is called when button is pressed while already toggled.
        """
        return False

    def _on_unhover(self, x: int, y: int, dx: int, dy: int) -> None:
        """Change the button color and call the on_unhover callback."""
        super(Button, self)._on_unhover(x, y, dx, dy)
        if self.definition.hover_color is not None:
            # Reset the color back to what is should be based on the toggled state.
            if not self._is_toggled:
                self.color_rect.color = self.definition.base_color.as_tuple()
            elif self.definition.depressed_color is not None:
                self.color_rect.color = self.definition.depressed_color.as_tuple()
