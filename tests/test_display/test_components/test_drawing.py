"""Tests for the drawing components."""

from shimmer.display.components.drawing import (
    RectDrawingBoxDefinition,
    RectDrawingBox,
)


def test_rect_drawing_box(run_gui, updatable_text_box):
    """You should be able to drag out rects with the mouse, and the rect should be printed."""
    text_box, update_text_box = updatable_text_box

    defn = RectDrawingBoxDefinition(on_complete=update_text_box)
    box = RectDrawingBox(defn)
    assert run_gui(test_rect_drawing_box, text_box, box)
