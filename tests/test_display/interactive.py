"""Module defining test helpers for interactive GUI testing."""

from dataclasses import replace
from textwrap import dedent
from typing import Optional

import cocos
from shimmer.display.alignment import LeftBottom, LeftTop
from shimmer.display.components.box import ActiveBox, BoxDefinition
from shimmer.display.components.font import Calibri
from shimmer.display.keyboard import (
    KeyboardHandler,
    KeyboardHandlerDefinition,
)
from shimmer.display.widgets.text_box import TextBox, TextBoxDefinition


class PassOrFailInput(ActiveBox):
    """Handler to control pass/fail of test by user pressing Y/N."""

    def __init__(self, test_name: str, test_description: Optional[str] = None):
        """
        Create a PassOrFailInput.

        :param test_name: Name of the test to display.
        :param test_description: Description of the test to display.
        """
        window_width, window_height = cocos.director.director.get_window_size()
        definition = BoxDefinition(width=window_width, height=window_height)
        super(PassOrFailInput, self).__init__(definition)
        self.passed: bool = False
        name = TextBox(
            TextBoxDefinition(text=test_name, font=replace(Calibri, bold=True),)
        )
        description = TextBox(
            TextBoxDefinition(
                text=dedent(test_description or "").strip(), width=window_width,
            )
        )
        keyboard_handler_definition = KeyboardHandlerDefinition(focus_required=False)
        keyboard_handler_definition.add_keyboard_action_simple(
            "n", self.fail_test,
        )
        keyboard_handler_definition.add_keyboard_action_simple(
            "y", self.pass_test,
        )
        keyboard_handler = KeyboardHandler(keyboard_handler_definition)
        self.add(name)
        self.add(description)
        self.add(keyboard_handler)
        name.position = (0, window_height - name.rect.height)
        description.align_anchor_with_other_anchor(name, LeftBottom, LeftTop)

    def fail_test(self):
        """Mark the test as failed and close the window."""
        self.passed = False
        cocos.director.director.pop()
        return True

    def pass_test(self):
        """Mark the test as passed and close the window."""
        self.passed = True
        cocos.director.director.pop()
        return True


class SimpleEventLayer(cocos.layer.Layer):
    """Simple cocos layer that can hold children and activate events on them."""

    is_event_handler = True

    def __init__(self, *children):
        """
        Create a SimpleEventLayer and activate events on all children.

        :param children: CocosNodes to enable events for.
        """
        super(SimpleEventLayer, self).__init__()
        for child in children:
            self.add(child)
