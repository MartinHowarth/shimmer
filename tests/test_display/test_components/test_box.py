"""
Tests for the MouseBox component.

Performs tests with a mock GUI to check event handling is correct.
"""

import cocos
from shimmer.display.alignment import ZIndexEnum
from shimmer.display.components.box import (
    Box,
    BoxDefinition,
    bounding_rect_of_rects,
    DynamicSizeBehaviourEnum,
)


def make_dummy_box() -> Box:
    """Make a dummy box for use in tests."""
    box = Box(BoxDefinition(width=100, height=100))
    box.position = 100, 100
    return box


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

    rect = bounding_rect_of_rects((box.world_rect for box in boxes))

    assert rect == cocos.rect.Rect(100, 100, 300, 300)


def test_dynamic_width_fit_children(mock_gui, subtests):
    """Test box dynamic width resizing."""
    box = Box(
        BoxDefinition(
            width=None,
            height=100,
            dynamic_size_behaviour=DynamicSizeBehaviourEnum.fit_children,
        )
    )
    child = Box(BoxDefinition(width=100, height=1000))
    child2 = Box(BoxDefinition(width=500, height=1000))

    with subtests.test("Test that fit_children defaults sensibly with no children."):
        assert box.rect == cocos.rect.Rect(0, 0, 0, 100)

    with subtests.test("Test that adding a child automatically resizes the parent."):
        box.add(child)
        # Only the width should update to fit the child; not the height.
        assert box.rect == cocos.rect.Rect(0, 0, 100, 100)

    with subtests.test(
        "Test that adding a second child automatically resizes the parent."
    ):
        box.add(child2)
        assert box.rect == cocos.rect.Rect(0, 0, 500, 100)

    with subtests.test("Test that removing a child automatically resizes the parent."):
        box.remove(child2)
        assert box.rect == cocos.rect.Rect(0, 0, 100, 100)

    with subtests.test(
        "Test that removing all children automatically resizes the parent."
    ):
        box.remove(child)
        assert box.rect == cocos.rect.Rect(0, 0, 0, 100)


def test_dynamic_height_fit_children(mock_gui, subtests):
    """Test box dynamic height resizing."""
    box = Box(
        BoxDefinition(
            width=100,
            height=None,
            dynamic_size_behaviour=DynamicSizeBehaviourEnum.fit_children,
        )
    )
    child = Box(BoxDefinition(width=1000, height=100))
    child2 = Box(BoxDefinition(width=1000, height=500))

    with subtests.test("Test that fit_children defaults sensibly with no children."):
        assert box.rect == cocos.rect.Rect(0, 0, 100, 0)

    with subtests.test("Test that adding a child automatically resizes the parent."):
        box.add(child)
        # Only the width should update to fit the child; not the height.
        assert box.rect == cocos.rect.Rect(0, 0, 100, 100)

    with subtests.test(
        "Test that adding a second child automatically resizes the parent."
    ):
        box.add(child2)
        assert box.rect == cocos.rect.Rect(0, 0, 100, 500)

    with subtests.test("Test that removing a child automatically resizes the parent."):
        box.remove(child2)
        assert box.rect == cocos.rect.Rect(0, 0, 100, 100)

    with subtests.test(
        "Test that removing all children automatically resizes the parent."
    ):
        box.remove(child)
        assert box.rect == cocos.rect.Rect(0, 0, 100, 0)


def test_width_and_height_dynamic_size_fit_children(mock_gui, subtests):
    """Test that both width and height can be dynamically sized simultaneously."""
    box = Box(
        BoxDefinition(
            width=None,
            height=None,
            dynamic_size_behaviour=DynamicSizeBehaviourEnum.fit_children,
        )
    )
    assert box.rect == cocos.rect.Rect(0, 0, 0, 0)

    with subtests.test("Test that adding a child updates both width and height."):
        child = Box(BoxDefinition(width=1000, height=100))
        box.add(child)
        assert box.rect == cocos.rect.Rect(0, 0, 1000, 100)

    with subtests.test("Test that resizing the child updates the width and height."):
        child.definition = BoxDefinition(width=300, height=400)
        child.update_rect()
        assert box.rect == cocos.rect.Rect(0, 0, 300, 400)


def test_width_and_height_dynamic_size_match_parent(mock_gui, subtests):
    """Test that both width and height can be dynamically sized simultaneously."""
    child = Box(
        BoxDefinition(
            width=None,
            height=None,
            dynamic_size_behaviour=DynamicSizeBehaviourEnum.match_parent,
        )
    )
    parent = Box(BoxDefinition(width=1000, height=100))
    assert child.rect == cocos.rect.Rect(0, 0, 0, 0)

    with subtests.test(
        "Test that adding the child causes the child to match the parent."
    ):
        parent.add(child)
        assert child.rect == cocos.rect.Rect(0, 0, 1000, 100)

    with subtests.test("Test that resizing the parent causes the child to resize."):
        parent.definition = BoxDefinition(width=300, height=400)
        parent.update_rect()
        assert child.rect == cocos.rect.Rect(0, 0, 300, 400)


def test_ignore_child_size_if_dynamically_matches_parent(mock_gui, subtests):
    """Test that a dynamic child and a dynamic parent interact correctly."""
    child = Box(
        BoxDefinition(
            width=None,
            height=100,
            dynamic_size_behaviour=DynamicSizeBehaviourEnum.match_parent,
        )
    )
    parent = Box(
        BoxDefinition(
            width=300,
            height=None,
            dynamic_size_behaviour=DynamicSizeBehaviourEnum.fit_children,
        )
    )
    parent.add(child)

    # The child should match the parents width; and the parent should fit the childs height.
    assert child.rect == cocos.rect.Rect(0, 0, 300, 100)
    assert parent.rect == cocos.rect.Rect(0, 0, 300, 100)
