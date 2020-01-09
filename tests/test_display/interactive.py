"""Module defining test helpers for interactive GUI testing."""

import cocos
import pyglet

from textwrap import dedent
from typing import Optional


class PassOrFailInput(cocos.layer.Layer):
    """Handler to control pass/fail of test by user pressing Y/N."""

    is_event_handler = True

    def __init__(self, test_name: str, test_description: Optional[str] = None):
        """
        Create a PassOrFailInput cocos layer.

        :param test_name: Name of the test to display.
        :param test_description: Description of the test to display.
        """
        super(PassOrFailInput, self).__init__()
        self.passed: bool = False
        name = cocos.text.Label(
            test_name,
            font_name="calibri",
            font_size=16,
            bold=True,
            anchor_x="left",
            anchor_y="top",
        )
        name.position = 0, cocos.director.director.get_window_size()[1]
        description = cocos.text.RichLabel(
            dedent(test_description or "").strip(),
            font_name="calibri",
            font_size=14,
            anchor_x="left",
            anchor_y="top",
            multiline=True,
            width=cocos.director.director.get_window_size()[0],
        )
        description.position = 0, cocos.director.director.get_window_size()[1] - 20
        self.add(name)
        self.add(description)

    def on_key_press(self, key, modifiers):
        """Handle user key presses to flag pass or failure of the test."""
        if key == pyglet.window.key.N:
            self.passed = False
            cocos.director.director.pop()
        elif key == pyglet.window.key.Y:
            self.passed = True
            cocos.director.director.pop()


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
