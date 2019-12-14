import cocos
import pytest

from shimmer.display.data_structures import Color
from shimmer.display.widgets.button import VisibleButtonDefinition, VisibleButton


@pytest.fixture
def visible_button_definition():
    return VisibleButtonDefinition(
        text="Click me!",
        base_color=Color(0, 120, 255),
        depressed_color=Color(0, 80, 255),
        hover_color=Color(0, 200, 255),
    )


def test_visible_button(run_gui, visible_button_definition):
    """Button that changes color and label when interacted with."""
    layer = VisibleButton(visible_button_definition)
    layer.rect = cocos.rect.Rect(0, 0, 100, 100)

    def change_text_callback(label):
        def inner(*_, **__):
            layer.definition.text = label
            layer.update_label()

        return inner

    layer.definition.on_press = change_text_callback("on_press")
    layer.definition.on_release = change_text_callback("on_release")
    layer.definition.on_hover = change_text_callback("on_hover")
    layer.definition.on_unhover = change_text_callback("on_unhover")

    assert run_gui(test_visible_button, layer)


def test_overlapping_buttons(run_gui, visible_button_definition):
    """Overlapping buttons should be independently interactable."""
    button1 = VisibleButton(visible_button_definition)
    button1.rect = cocos.rect.Rect(0, 0, 100, 100)
    button2 = VisibleButton(visible_button_definition)
    button2.rect = cocos.rect.Rect(0, 0, 100, 100)
    button2.position = 50, 50

    assert run_gui(test_overlapping_buttons, button1, button2)
