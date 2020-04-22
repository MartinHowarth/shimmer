"""Test the draggable Box."""

from dataclasses import replace
from typing import no_type_check

from mock import MagicMock

from shimmer.components.box import Box, BoxDefinition
from shimmer.components.draggable_box import (
    DragParentBox,
    DraggableBoxDefinition,
    SnapBox,
    SnapBoxDefinition,
)
from shimmer.data_structures import Color


# TODO test drag callbacks
# TODO test boundary box with mock gui
# TODO test direct draggable vs parent draggable (with boundary too)
def create_base_box() -> Box:
    """Create a Box that has a background color."""
    box = Box(BoxDefinition(width=100, height=100, background_color=Color(100, 20, 20)))
    return box


def test_draggable_box(run_gui):
    """The box should be a draggable."""
    base_box = create_base_box()
    box = DragParentBox(
        DraggableBoxDefinition(width=base_box.rect.width, height=base_box.rect.height)
    )

    base_box.add(box)

    assert run_gui(test_draggable_box, base_box)


def test_draggable_box_with_boundary(run_gui):
    """The box should be a draggable but bounded inside the grey box."""
    base_box = create_base_box()
    boundary_box = Box(
        BoxDefinition(width=450, height=200, background_color=Color(50, 50, 50))
    )
    box = DragParentBox(
        DraggableBoxDefinition(
            width=base_box.rect.width,
            height=base_box.rect.height,
            bounding_box=boundary_box,
        )
    )

    base_box.add(box)

    assert run_gui(test_draggable_box_with_boundary, boundary_box, base_box)


def test_draggable_box_no_gui(subtests, mock_gui, mock_mouse):
    """Test that the draggable box changes position of parent."""
    base_box = create_base_box()
    base_box.position = 10, 10
    box = DragParentBox(
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
        snap_box = SnapBox(
            SnapBoxDefinition(width=10, height=10, background_color=Color(255, 0, 0))
        )
        snap_box.position = 150 * i, 150 * i
        snap_points.append(snap_box)

    base_box = create_base_box()
    box = DragParentBox(
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
    """Test that draggable box sets position correctly when dragged over snap points."""
    snap_box = SnapBox(SnapBoxDefinition(width=10, height=10))
    snap_box.position = 110, 110

    base_box = create_base_box()
    box = DragParentBox(
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


@no_type_check  # Ignore typing because Mocks don't type nicely.
def test_snap_box_can_receive(subtests, mock_gui, mock_mouse):
    """Test that SnapBox can_receive callback is used correctly by DraggableBox."""
    snap_box = SnapBox(
        SnapBoxDefinition(width=10, height=10, can_receive=MagicMock(return_value=True))
    )
    snap_box.position = 110, 110

    base_box = create_base_box()
    drag_box = DragParentBox(
        DraggableBoxDefinition(
            width=base_box.rect.width,
            height=base_box.rect.height,
            snap_boxes=[snap_box],
        )
    )

    base_box.add(drag_box)
    base_box.position = 0, 0

    with subtests.test(
        "Dragging over the snap box causes the box to snap to it and can_receive is called."
    ):
        mock_mouse.click_and_drag(drag_box, (20, 20), (40, 40))
        assert base_box.position == (65, 65)
        assert snap_box.is_occupied is True
        snap_box.definition.can_receive.assert_called_with(drag_box)

    base_box.position = 0, 0
    drag_box.unsnap_if_snapped()
    snap_box.definition.can_receive.reset_mock()

    snap_box.definition = replace(
        snap_box.definition, can_receive=MagicMock(return_value=False)
    )

    with subtests.test(
        "Dragging over the snap box does not cause a snap because can_receive returns False."
    ):
        mock_mouse.click_and_drag(drag_box, (20, 20), (40, 40))
        assert base_box.position == (20, 20)  # Didn't snap, but still got dragged.
        assert snap_box.is_occupied is False
        snap_box.definition.can_receive.assert_called_with(drag_box)


@no_type_check  # Ignore typing because Mocks don't type nicely.
def test_snap_box_on_receive_on_release(subtests, mock_gui):
    """Test that SnapBox calls its defined callbacks when a DraggableBox interacts with it."""
    snap_box = SnapBox(
        SnapBoxDefinition(
            width=10, height=10, on_receive=MagicMock(), on_release=MagicMock(),
        )
    )

    base_box = create_base_box()
    drag_box = DragParentBox(
        DraggableBoxDefinition(
            width=base_box.rect.width,
            height=base_box.rect.height,
            snap_boxes=[snap_box],
        )
    )

    base_box.add(drag_box)
    base_box.position = 0, 0

    with subtests.test(
        "Test that on_receive is called when a drag box snaps onto a SnapBox."
    ):
        drag_box.snap_to(snap_box)
        snap_box.definition.on_receive.assert_called_with(drag_box)
        snap_box.definition.on_release.assert_not_called()
        assert snap_box.is_occupied is True

    snap_box.definition.on_receive.reset_mock()

    with subtests.test(
        "Test that on_receive is not called a second time when a drag box snaps "
        "onto the same SnapBox."
    ):
        drag_box.snap_to(snap_box)
        snap_box.definition.on_receive.assert_not_called()
        snap_box.definition.on_release.assert_not_called()
        assert snap_box.is_occupied is True

    snap_box.definition.on_receive.reset_mock()

    with subtests.test("Test that on_release is called when a draggable box unsnaps."):
        drag_box.unsnap_if_snapped()
        snap_box.definition.on_release.assert_called_with(drag_box)
        snap_box.definition.on_receive.assert_not_called()
        assert snap_box.is_occupied is False

    snap_box.definition.on_release.reset_mock()

    with subtests.test(
        "Test that on_release is not called when a draggable box is not currently snapped."
    ):
        drag_box.unsnap_if_snapped()
        snap_box.definition.on_release.assert_not_called()
        snap_box.definition.on_receive.assert_not_called()
        assert snap_box.is_occupied is False


@no_type_check  # Ignore typing because Mocks don't type nicely.
def test_must_be_snapped(subtests, mock_gui, mock_mouse):
    """Test that "must_be_snapped" results in a DraggableBox that is always snapped."""
    snap_box = SnapBox(SnapBoxDefinition(width=10, height=10))
    snap_box.position = 110, 110
    snap_box2 = SnapBox(SnapBoxDefinition(width=10, height=10))
    snap_box2.position = 310, 310

    base_box = create_base_box()
    drag_box = DragParentBox(
        DraggableBoxDefinition(
            width=base_box.rect.width,
            height=base_box.rect.height,
            snap_on_release=True,
            snap_boxes=[snap_box, snap_box2],
        )
    )

    base_box.add(drag_box)
    base_box.position = 0, 0

    # Set the drag box as initially snapped to snap box 1.
    drag_box.snap_to(snap_box)
    assert base_box.position == (65, 65)

    with subtests.test(
        "Dragging the drag box off snap 1, but not over snap 2 results in the drag "
        "box returning to be snapped over snap1."
    ):
        # Drag really far away to ensure we don't overlap with snap2.
        mock_mouse.click_and_drag(drag_box, (65, 65), (1000, 1000))
        assert base_box.position == (65, 65)
        assert snap_box.is_occupied is True
        assert snap_box2.is_occupied is False

    with subtests.test(
        "Dragging the drag box off snap 1 and over snap2 results in being snapped to snap2."
    ):
        # Drag really far away to ensure we don't overlap with snap2.
        mock_mouse.click_and_drag(drag_box, (100, 100), (300, 300))
        assert base_box.position == (265, 265)
        assert snap_box.is_occupied is False
        assert snap_box2.is_occupied is True
