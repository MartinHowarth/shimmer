"""Test the button widget."""

import pytest

from dataclasses import replace
from mock import MagicMock
from typing import Any, no_type_check

from shimmer.display.data_structures import Color
from shimmer.display.widgets.button import ButtonDefinition, Button, ToggleButton


@pytest.fixture
def button_definition():
    """Common definition of a button for use in the tests."""
    return ButtonDefinition(
        text="Click me!",
        base_color=Color(0, 120, 255),
        depressed_color=Color(0, 80, 255),
        hover_color=Color(0, 200, 255),
        width=100,
        height=100,
    )


def change_text_callback(label):
    """Create a callback to change the text of a Button when it is interacted with."""

    def inner(box: Button, *_: Any, **__: Any) -> None:
        box.definition = replace(box.definition, text=label)
        box.update_label()

    return inner


def test_button(run_gui, button_definition):
    """Button that changes color and label when interacted with."""
    defn = replace(
        button_definition,
        on_press=change_text_callback("on_press"),
        on_release=change_text_callback("on_release"),
        on_hover=change_text_callback("on_hover"),
        on_unhover=change_text_callback("on_unhover"),
    )
    layer = Button(defn)

    assert run_gui(test_button, layer)


def test_overlapping_buttons(run_gui, button_definition):
    """Overlapping buttons should be independently interactable."""
    button1 = Button(button_definition)
    button2 = Button(button_definition)
    button2.position = 50, 50

    assert run_gui(test_overlapping_buttons, button1, button2)


def test_button_dynamic_size(run_gui, button_definition):
    """Button whose size always exactly fits the text on it."""
    defn = replace(
        button_definition,
        on_press=change_text_callback("on_press"),
        on_release=change_text_callback("on_release"),
        on_hover=change_text_callback("on_hover"),
        on_unhover=change_text_callback("on_unhover"),
        dynamic_size=True,
    )
    layer = Button(defn)

    assert run_gui(test_button_dynamic_size, layer)


def test_toggle_button(run_gui, button_definition):
    """The button should toggle on/off when clicked."""
    defn = replace(
        button_definition,
        hover_color=None,
        on_press=change_text_callback("On"),
        on_release=change_text_callback("Off"),
    )
    layer = ToggleButton(defn)

    assert run_gui(test_toggle_button, layer)


@no_type_check  # Ignore typing because Mocks don't type nicely.
def test_toggle_button_no_gui(subtests, mock_gui, mock_mouse):
    """Test the functionality of a toggle button without the graphical components."""
    button = ToggleButton(
        ButtonDefinition(
            width=100,
            height=100,
            on_press=MagicMock(return_value=True),
            on_release=MagicMock(return_value=True),
        )
    )

    with subtests.test("Test that the first click calls `on_press` only."):
        mock_mouse.click(button)
        button.definition.on_release.assert_not_called()
        button.definition.on_press.assert_called_once()
        assert button.is_toggled is True

    button.definition.on_press.reset_mock()

    with subtests.test("Test that the second click calls `on_release` only."):
        mock_mouse.click(button)
        button.definition.on_release.assert_called_once()
        button.definition.on_press.assert_not_called()
        assert button.is_toggled is False

    button.definition.on_release.reset_mock()

    with subtests.test("Test that the third click calls `on_press` only."):
        mock_mouse.click(button)
        button.definition.on_release.assert_not_called()
        button.definition.on_press.assert_called_once()
        assert button.is_toggled is True
