"""Test the selection system components."""

from typing import Callable, Optional

from shimmer.display.primitives import create_color_rect
from shimmer.display.data_structures import ActiveGreen, PassiveBlue, Color
from shimmer.display.components.selection import (
    SelectableBox,
    SelectionDrawingBox,
    SelectableBoxDefinition,
    MouseDefinedRect,
)


def make_dummy_selection_point(x: int, y: int) -> SelectableBox:
    """Create a SelectableBox at the given coordinates that changes color when selected."""
    color_layer = create_color_rect(30, 30, PassiveBlue)

    def change_color(color: Color) -> Callable[[Optional[MouseDefinedRect]], None]:
        def inner(*_, **__):
            nonlocal color_layer
            color_layer.color = color.as_tuple()

        return inner

    box = SelectableBox(
        SelectableBoxDefinition(
            width=30,
            height=30,
            on_highlight=change_color(Color(200, 200, 0)),
            on_unhighlight=change_color(PassiveBlue),
            on_select=change_color(ActiveGreen),
            on_deselect=change_color(PassiveBlue),
        )
    )
    box.position = x, y
    box.add(color_layer)
    return box


def test_drag_to_select(run_gui):
    """
    You should be able to drag out rects with the mouse.

    The squares should change color when included in the selection.
    """
    boxes = [make_dummy_selection_point(i * 50, i * 50) for i in range(5)]
    selection_box = SelectionDrawingBox()
    assert run_gui(test_drag_to_select, selection_box, *boxes)
