"""Test the button widget."""

import cocos
import pytest

from dataclasses import replace

from shimmer.display.data_structures import Color
from shimmer.display.widgets.button import ButtonDefinition, Button


@pytest.fixture
def button_definition():
    """Common definition of a button for use in the tests."""
    return ButtonDefinition(
        text="Click me!",
        base_color=Color(0, 120, 255),
        depressed_color=Color(0, 80, 255),
        hover_color=Color(0, 200, 255),
    )


def test_button(run_gui, button_definition):
    """Button that changes color and label when interacted with."""

    def change_text_callback(label):
        def inner(parent: Button, *_, **__):
            parent.definition = replace(parent.definition, text=label)
            parent.update_label()

        return inner

    defn = replace(
        button_definition,
        on_press=change_text_callback("on_press"),
        on_release=change_text_callback("on_release"),
        on_hover=change_text_callback("on_hover"),
        on_unhover=change_text_callback("on_unhover"),
    )
    layer = Button(defn, cocos.rect.Rect(0, 0, 100, 100))

    assert run_gui(test_button, layer)


def test_overlapping_buttons(run_gui, button_definition):
    """Overlapping buttons should be independently interactable."""
    button1 = Button(button_definition, cocos.rect.Rect(0, 0, 100, 100))
    button2 = Button(button_definition, cocos.rect.Rect(0, 0, 100, 100))
    button2.position = 50, 50

    assert run_gui(test_overlapping_buttons, button1, button2)


def test_button_dynamic_size(run_gui, button_definition):
    """Button whose size always exactly fits the text on it."""

    def change_text_callback(label):
        def inner(parent: Button, *_, **__):
            parent.definition = replace(parent.definition, text=label)
            parent.update_label()

        return inner

    defn = replace(
        button_definition,
        on_press=change_text_callback("on_press"),
        on_release=change_text_callback("on_release"),
        on_hover=change_text_callback("on_hover"),
        on_unhover=change_text_callback("on_unhover"),
    )
    layer = Button(defn, rect=None)

    assert run_gui(test_button_dynamic_size, layer)
