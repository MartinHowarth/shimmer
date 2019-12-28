"""
Tests for the MouseBox component.

Performs tests with a mock GUI to check event handling is correct.
"""

import cocos

from shimmer.display.components.box import Box, BoxDefinition, bounding_rect_of_boxes
from shimmer.display.data_structures import ZIndexEnum


def make_dummy_box() -> Box:
    """Make a dummy box for use in tests."""
    box = Box(BoxDefinition(width=100, height=100))
    box.position = 100, 100
    return box


def test_box_changing_rect(subtests, mock_gui):
    """Test that the box position updates correctly when the rect is changed."""
    box = make_dummy_box()

    with subtests.test("Check position of box is set to origin of rect."):
        assert box.position == (100, 100)

    with subtests.test("When changing rect, position gets updated."):
        box.rect = cocos.rect.Rect(50, 50, 100, 100)
        assert box.position == (50, 50)
        assert box.rect == cocos.rect.Rect(0, 0, 100, 100)


def test_box_point_to_world(mock_gui):
    """Test that translating a point into world coordinate space works."""
    box = make_dummy_box()
    assert box.point_to_world((10, 10)) == (110, 110)


def test_box_point_to_local(mock_gui):
    """Test that translating a point from world coordinate space works."""
    box = make_dummy_box()
    assert box.point_to_local((10, 10)) == (-90, -90)


def test_box_get_z_value(mock_gui):
    """Test that reading the z value of a Box from its parent works."""
    box = make_dummy_box()
    parent = Box()
    parent.add(box, z=12)

    assert box.get_z_value() == 12


def test_box_set_z_value(subtests, mock_gui):
    """Test that setting the z value of a Box in its parent works."""
    box = make_dummy_box()
    box1 = make_dummy_box()
    box2 = make_dummy_box()
    parent = Box()
    parent.add(box1, z=(box1_index := 1))
    parent.add(box2, z=(box2_index := 2))
    parent.add(box, z=12)

    with subtests.test("Can set to precise value."):
        box.set_z_value(-2)
        assert box.get_z_value() == -2

    with subtests.test("Can set to highest in list."):
        box.set_z_value(ZIndexEnum.top)
        assert box.get_z_value() == box2_index + 1

    with subtests.test("No change when set to highest in list if already highest."):
        initial_z = box.get_z_value()
        box.set_z_value(ZIndexEnum.top)
        assert box.get_z_value() == initial_z

    with subtests.test("Can set to lowest in list."):
        box.set_z_value(ZIndexEnum.bottom)
        assert box.get_z_value() == box1_index - 1


def test_bounding_rect_of_boxes(mock_gui):
    """Test that calculating the bounding rect of a set of Boxes works correctly."""
    boxes = []
    for i in range(1, 4):
        box = make_dummy_box()
        box.position = 100 * i, 100 * i
        boxes.append(box)

    rect = bounding_rect_of_boxes(boxes)

    assert rect == cocos.rect.Rect(100, 100, 300, 300)
