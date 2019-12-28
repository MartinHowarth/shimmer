"""Test the draggable anchor Box."""

from shimmer.display.components.box import Box, BoxDefinition
from shimmer.display.components.draggable_anchor import DraggableAnchor
from shimmer.display.data_structures import Color


def create_base_box() -> Box:
    """Create a Box that has a background color."""
    box = Box(BoxDefinition(width=100, height=100, background_color=Color(100, 20, 20)))
    return box


def test_draggable_anchor(run_gui):
    """The box should be a draggable."""
    base_box = create_base_box()
    anchor = DraggableAnchor(base_box.rect)

    base_box.add(anchor)

    assert run_gui(test_draggable_anchor, base_box)


def test_draggable_anchor_no_gui(subtests, mock_gui, mock_mouse):
    """Test that the draggable anchor changes position of parent."""
    base_box = create_base_box()
    base_box.position = 10, 10
    anchor = DraggableAnchor(base_box.rect)
    base_box.add(anchor)

    assert base_box.position == (10, 10)
    mock_mouse.click_and_drag(anchor, (20, 20), (140, 260))
    assert base_box.position == (130, 250)
