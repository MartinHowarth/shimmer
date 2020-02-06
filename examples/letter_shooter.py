"""
An example of a point-and-shoot game where you have to shoot boxes with the correct letter.

This shows how to make use of focus-on-hover behaviour and keyboard handling.
"""
from dataclasses import dataclass, field
from random import randint, choice
from string import ascii_lowercase

import cocos
from shimmer.display.components.box import Box, BoxDefinition
from shimmer.display.components.focus import (
    FocusBoxDefinition,
    make_focusable,
    EVENT_HANDLED,
)
from shimmer.display.data_structures import Color
from shimmer.display.keyboard import add_simple_keyboard_handler
from shimmer.display.widgets.text_box import TextBoxDefinition, TextBox


@dataclass(frozen=True)
class TargetDefinition(BoxDefinition):
    """Definition of a target in this game."""

    key: str = field(default="a")


class Target(Box):
    """
    A Target that can be destroyed by shooting it with the keyboard.

    More specifically, this requires the user to move the mouse over the target, and then press
    the correct keyboard button.
    """

    def __init__(self, definition: TargetDefinition):
        """Create a new Target."""
        super(Target, self).__init__(definition)
        # Add a TextBox to display the required letter.
        self.text_box = TextBox(TextBoxDefinition(text=definition.key.upper()))
        self.add(self.text_box)
        # Position the text box in the center of this target.
        self.text_box.align_anchor_with_other_anchor(self)

        # Add a keyboard handler to listen for keyboard events.
        self.keyboard_handler = add_simple_keyboard_handler(
            self, definition.key, self._on_correct_keypress
        )

        # Add a focus box to make this target only listen to keyboard events when the mouse is
        # inside it. Use the "focus_on_hover" option to gain/lose focus when the mouse enters/leaves
        # the box.
        self.focus_box = make_focusable(self, FocusBoxDefinition(focus_on_hover=True))

    def _on_correct_keypress(self) -> bool:
        """On correct keypress, kill this target and create a new one."""
        self.kill()
        self.parent.add(create_random_target())
        return EVENT_HANDLED


def create_random_target() -> Target:
    """Create a Target with random size, position, color and letter."""
    window_width, window_height = cocos.director.director.get_window_size()
    max_target_width, max_target_height = 300, 300
    target_definition = TargetDefinition(
        width=randint(30, max_target_width),
        height=randint(30, max_target_height),
        background_color=Color(randint(50, 255), randint(50, 255), randint(50, 255)),
        key=choice(ascii_lowercase),
    )
    x, y = (
        randint(0, window_width - max_target_width),
        randint(0, window_height - max_target_height),
    )

    target = Target(target_definition)
    target.position = x, y
    return target


def main():
    """Run the Letter Shooter game."""
    cocos.director.director.init()
    initial_target = create_random_target()
    scene = cocos.scene.Scene(initial_target)
    cocos.director.director.run(scene)


if __name__ == "__main__":
    main()
