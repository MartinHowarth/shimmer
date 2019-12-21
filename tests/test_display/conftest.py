"""Module defining global pytest fixtures for GUI tests."""

import cocos
import pyglet
import pytest

from textwrap import dedent
from typing import Optional, List, Callable


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


@pytest.fixture
def run_gui():
    """Fixture to run graphical tests and get user input to pass/fail the test."""

    def run_scene(
        test_func: Callable, *children: List[cocos.cocosnode.CocosNode]
    ) -> bool:
        """
        Run a cocos director with the given test function description and display the children.

        Blocks until the user presses Y or N, or closes the director window.

        :param test_func: Reference to the test function to display name and docstring.
        :param children: Cocos nodes to display.
        :return: True if the user pressed 'Y', or False if they pressed 'N'.
        """
        input_handler = PassOrFailInput(test_func.__name__, test_func.__doc__)

        children_layer = SimpleEventLayer(*children)
        children_layer.position = 50, 50

        scene = cocos.scene.Scene(children_layer, input_handler)
        cocos.director.director.run(scene)
        return input_handler.passed

    window = cocos.director.director.init(resizable=True)
    cocos.director.director.show_FPS = True
    cocos.director.director.window.set_location(100, 100)
    yield run_scene
    cocos.director.director.terminate_app = True
    # Running director.init seems to re-create every window that has previously existed
    # (i.e. one per test). Not sure why it does that, but directly closing the window at the end
    # of the test fixes the problem.
    window.close()
