import cocos
import pytest

from shimmer.display.components.draggable_anchor import DraggableAnchor
from shimmer.display.components.button import (
    VisibleButtonDefinition,
    VisibleButton,
)
from shimmer.display.data_structures import Color


@pytest.fixture
def visible_button_definition():
    return VisibleButtonDefinition(
        text="Click me!",
        base_color=Color(0, 120, 255),
        depressed_color=Color(0, 80, 255),
        hover_color=Color(0, 200, 255),
    )


def test_draggable_anchor(run_gui, visible_button_definition):
    """Bottom-left quadrant of the button should be a draggable anchor for the entire Button."""
    button = VisibleButton(visible_button_definition, cocos.rect.Rect(0, 0, 100, 100))
    anchor = DraggableAnchor(cocos.rect.Rect(0, 0, 50, 50))

    button.add(anchor)

    assert run_gui(test_draggable_anchor, button)
