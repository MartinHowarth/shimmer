"""
A visible, clickable button.

Changes color when interacted with (clicked. on hover) and calls the defined methods.
"""

import logging
from dataclasses import dataclass
from typing import Optional

import cocos
from shimmer.display.components.mouse_box import (
    MouseBoxDefinition,
    MouseBox,
    EVENT_HANDLED,
)
from shimmer.display.data_structures import Color, PassiveBlue, ActiveBlue, MutedBlue
from shimmer.display.helpers import bitwise_contains
from shimmer.display.keyboard import (
    KeyboardActionDefinition,
    KeyboardHandlerDefinition,
    KeyboardHandler,
)
from shimmer.display.widgets.text_box import TextBoxDefinition, TextBox

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class ButtonDefinition(MouseBoxDefinition):
    """A Button definition with visual elements."""

    text: Optional[str] = None

    base_color: Color = PassiveBlue
    depressed_color: Optional[Color] = MutedBlue
    hover_color: Optional[Color] = ActiveBlue

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

    def __init__(self, definition: ButtonDefinition):
        """
        Create a new Button.

        :param definition: Definition of the button.
        """
        super(Button, self).__init__(definition)
        self.definition: ButtonDefinition = self.definition
        self.label: Optional[TextBox] = None
        self.keyboard_handler: Optional[KeyboardHandler] = None
        self.update_label()
        self._set_background_color(self.definition.base_color)
        self.update_keyboard_handler()

    @property
    def rect(self) -> cocos.rect.Rect:
        """Get the rect defining the shape of this button."""
        return self._rect

    def update_label(self):
        """Recreate the button label."""
        if self.label is not None:
            # Don't resize because the label is what controls a dynamically sized button,
            # so save the resizing to when we re-make the label.
            # If the label is just totally removed then there isn't a sensible size to resize
            # to anyway.
            self.remove(self.label, no_resize=True)

        if self.definition.formatted_text is None:
            self.label = None
            return

        self.label = TextBox(TextBoxDefinition(text=self.definition.formatted_text))
        self.add(self.label)
        if not self.definition.is_dynamic_sized:
            # If dynamic sized, then the label helps control setting the size, so it makes no
            # sense to align it.
            self.label.align_anchor_with_other_anchor(self)

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
        """Change the button color and call the on_select callback."""
        super(Button, self)._on_press(x, y, buttons, modifiers)
        if self.definition.depressed_color is not None:
            self._set_background_color(self.definition.depressed_color)
        return EVENT_HANDLED

    def _on_release(
        self, x: int, y: int, buttons: int, modifiers: int
    ) -> Optional[bool]:
        """Change the button color and call the on_release callback."""
        super(Button, self)._on_release(x, y, buttons, modifiers)
        if self._currently_hovered:
            if self.definition.hover_color is not None:
                self._set_background_color(self.definition.hover_color)
        else:
            self._set_background_color(self.definition.base_color)
        return EVENT_HANDLED

    def _on_hover(self, x: int, y: int, dx: int, dy: int) -> Optional[bool]:
        """Change the button color and call the on_hover callback."""
        result = super(Button, self)._on_hover(x, y, dx, dy)
        if self.definition.hover_color is not None:
            self._set_background_color(self.definition.hover_color)
        return result

    def _on_unhover(self, x: int, y: int, dx: int, dy: int) -> Optional[bool]:
        """Change the button color and call the on_unhover callback."""
        result = super(Button, self)._on_unhover(x, y, dx, dy)
        if self.definition.hover_color is not None:
            self._set_background_color(self.definition.base_color)
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
        activates on_select and on_release for this button on each key press.
        """
        self.keyboard_handler = None

        if self.definition.keyboard_shortcut is None:
            return

        keymap = KeyboardHandlerDefinition(
            logging_name=f"button[{self.definition.text}]"
        )
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

        Calls the on_select / on_release as appropriate.
        """
        if self._is_toggled != value:
            # If requested state is different to current state, then toggle this button.
            self._on_press(0, 0, 0, 0)
        # Otherwise no action needed to toggle the button.

    def _on_press(self, x: int, y: int, buttons: int, modifiers: int) -> None:
        """
        Called when the Box is clicked by the user.

        Alternatively calls the `on_select` and `on_release` callback from the definition on each
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
                self._set_background_color(self.definition.base_color)
            elif self.definition.depressed_color is not None:
                self._set_background_color(self.definition.depressed_color)
