"""Test the draggable box Box."""

from shimmer.display.components.box import Box, BoxDefinition
from shimmer.display.components.draggable_box import (
    DraggableBox,
    DraggableBoxDefinition,
)
from shimmer.display.data_structures import Color


def create_base_box() -> Box:
    """Create a Box that has a background color."""
    box = Box(BoxDefinition(width=100, height=100, background_color=Color(100, 20, 20)))
    return box


def test_draggable_box(run_gui):
    """The box should be a draggable."""
    base_box = create_base_box()
    box = DraggableBox(
        DraggableBoxDefinition(width=base_box.rect.width, height=base_box.rect.height)
    )

    base_box.add(box)

    assert run_gui(test_draggable_box, base_box)


def test_draggable_box_no_gui(subtests, mock_gui, mock_mouse):
    """Test that the draggable box changes position of parent."""
    base_box = create_base_box()
    base_box.position = 10, 10
    box = DraggableBox(
        DraggableBoxDefinition(width=base_box.rect.width, height=base_box.rect.height)
    )
    base_box.add(box)

    assert base_box.position == (10, 10)
    mock_mouse.click_and_drag(box, (20, 20), (140, 260))
    assert base_box.position == (130, 250)


def test_draggable_box_snap_to_box(run_gui):
    """The box should be a draggable and should snap to the red boxes."""
    snap_points = []
    for i in range(3):
        snap_box = Box(
            BoxDefinition(width=10, height=10, background_color=Color(255, 0, 0))
        )
        snap_box.position = 150 * i, 150 * i
        snap_points.append(snap_box)

    base_box = create_base_box()
    box = DraggableBox(
        DraggableBoxDefinition(
            width=base_box.rect.width,
            height=base_box.rect.height,
            snap_boxes=snap_points,
        )
    )

    base_box.add(box)
    base_box.position = (300, 0)

    assert run_gui(test_draggable_box_snap_to_box, base_box, *snap_points)


def test_draggable_box_snap_to_box_no_gui(subtests, mock_gui, mock_mouse):
    """Test that draggable boc sets position correctly when dragged over snap points."""
    snap_box = Box(BoxDefinition(width=10, height=10))
    snap_box.position = 110, 110

    base_box = create_base_box()
    box = DraggableBox(
        DraggableBoxDefinition(
            width=base_box.rect.width,
            height=base_box.rect.height,
            snap_boxes=[snap_box],
        )
    )

    base_box.add(box)
    base_box.position = 0, 0

    with subtests.test(
        "Dragging over the snap box causes the box to snap to the center of it."
    ):
        mock_mouse.click_and_drag(box, (20, 20), (40, 40))
        assert base_box.position == (65, 65)

    with subtests.test(
        "Dragging a small amount does not move the box because still snapped."
    ):
        mock_mouse.click_and_drag(box, (70, 70), (75, 75))
        assert base_box.position == (65, 65)
        mock_mouse.click_and_drag(box, (80, 80), (75, 75))
        assert base_box.position == (65, 65)

    with subtests.test(
        "Dragging off the snap box allows the box to move freely again."
    ):
        mock_mouse.click_and_drag(box, (70, 70), (170, 170))
        assert base_box.position == (165, 165)

    with subtests.test(
        "Dragging without releasing the mouse should allow fine control of snap "
        "and release near edge of snap box."
    ):
        base_box.position = (0, 0)
        mock_mouse.press(box, (95, 95))
        mock_mouse.drag(box, (95, 95), (110, 110))
        assert base_box.position == (65, 65)
        mock_mouse.drag(box, (110, 110), (97, 97))
        assert base_box.position == (2, 2)
        mock_mouse.release(box)
