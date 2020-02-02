"""Module defining global pytest fixtures for GUI tests."""

import os
from typing import Callable, List, Tuple, Any

import pytest

import cocos
from shimmer.display.widgets.text_box import TextBox, TextBoxDefinition
from tests.test_display.mock_window import MockWindow
from .interactive import PassOrFailInput, SimpleEventLayer
from .mock_director import MockDirector
from .mock_keyboard import MockKeyboard
from .mock_mouse import MockMouse

SKIP_GUI_TESTS = "SKIP_GUI_TESTS" in os.environ


@pytest.fixture
def mock_gui(mocker):
    """Mock out the reliance of cocos on graphical elements existing."""
    # Have to patch director everywhere it's imported unfortunately.
    mock_director = MockDirector()
    mocker.patch("cocos.director.director", new=mock_director)
    mocker.patch("cocos.camera.director", new=mock_director)
    mocker.patch("cocos.layer.base_layers.director", new=mock_director)
    mocker.patch("cocos.layer.util_layers.director", new=mock_director)
    mocker.patch("pyglet.window.Window", new=MockWindow)

    # Make sure we've patched them correctly. This is mostly just future-proofing against
    # refactors in pyglet or cocos.
    assert issubclass(cocos.director.window.Window, MockWindow)

    # Disable autoscale so cocos doesn't try and use gl to scale the window.
    cocos.director.director.init(autoscale=False)


@pytest.fixture
def mock_mouse():
    """Fixture to provide a mock hardware mouse for tests to simulate mouse events."""
    return MockMouse()


@pytest.fixture
def mock_keyboard():
    """Fixture to provide a mock hardware keyboard for tests to simulate keyboard events."""
    return MockKeyboard()


@pytest.fixture
def run_gui():
    """Fixture to run graphical tests and get user input to pass/fail the test."""
    if SKIP_GUI_TESTS:
        pytest.skip(f"Test skipped because `SKIP_GUI_TESTS` is set in environment.")

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

        scene = cocos.scene.Scene(input_handler, children_layer)
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


@pytest.fixture
def updatable_text_box() -> Tuple[TextBox, Callable[[Any], None]]:
    """Fixture to create a text box whose text can be updated using the given callback."""
    text_box = TextBox(TextBoxDefinition(text="<placeholder>", width=500))
    text_box.position = 0, 300

    def update_text_box(text: Any) -> None:
        nonlocal text_box
        text_box.set_text(str(text))

    return text_box, update_text_box
