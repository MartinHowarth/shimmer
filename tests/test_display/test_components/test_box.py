"""
Tests for the MouseBox component.

Performs tests with a mock GUI to check event handling is correct.
"""
import logging
from typing import Tuple, Union

import pytest

import cocos
from shimmer.alignment import PositionalAnchor, CenterCenter, RightBottom, LeftTop
from shimmer.alignment import ZIndexEnum
from shimmer.components.box import (
    Box,
    BoxDefinition,
    bounding_rect_of_rects,
    DynamicSizeBehaviourEnum,
)
from shimmer.data_structures import White, Black


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


def test_box_get_z_value(mock_gui, subtests):
    """Test that reading the z value of a Box from its parent works."""
    box = make_dummy_box()

    with subtests.test("get_z_value returns None if there is no parent."):
        assert box.get_z_value() is None

    parent = Box()
    parent.add(box, z=12)

    with subtests.test("get_z_value returns correct z value."):
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

    with subtests.test("No change when set to lowest in list if already lowest."):
        initial_z = box.get_z_value()
        box.set_z_value(ZIndexEnum.bottom)
        assert box.get_z_value() == initial_z


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


@pytest.mark.parametrize("width,height", [(None, 100), [300, None]])
def test_ignore_child_size_if_dynamically_matches_parent(
    mock_gui, subtests, width, height
):
    """Test that a dynamic child and a dynamic parent interact correctly."""
    desired_width = width or 300
    desired_height = height or 100

    child = Box(
        BoxDefinition(
            width=width,
            height=desired_height,
            dynamic_size_behaviour=DynamicSizeBehaviourEnum.match_parent,
        )
    )
    parent = Box(
        BoxDefinition(
            width=desired_width,
            height=height,
            dynamic_size_behaviour=DynamicSizeBehaviourEnum.fit_children,
        )
    )
    parent.add(child)

    # The child should match the parents width; and the parent should fit the childs height.
    assert child.rect == cocos.rect.Rect(0, 0, desired_width, desired_height)
    assert parent.rect == cocos.rect.Rect(0, 0, desired_width, desired_height)


@pytest.mark.parametrize(
    "anchor1,anchor2,spacing,expected_xy",
    [
        pytest.param(CenterCenter, None, 0, (450, 450), id="default"),
        pytest.param(RightBottom, None, 0, (900, 0), id="RightBottom alignment"),
        pytest.param(
            RightBottom, LeftTop, 0, (1000, -100), id="Align different anchor points"
        ),
        pytest.param(
            CenterCenter, None, 100, (450, 450), id="CenterCenter spacing is ignored"
        ),
        pytest.param(
            RightBottom,
            None,
            50,
            (864, 35),
            id="RightBottom alignment with integer spacing",
        ),
        pytest.param(
            RightBottom,
            None,
            (50, 50),
            (950, 50),
            id="RightBottom alignment with exact (Tuple) spacing",
        ),
        pytest.param(
            RightBottom,
            None,
            cocos.draw.Vector2(-50, -50),
            (850, -50),
            id="RightBottom alignment with exact (Vector2) spacing",
        ),
    ],
)
def test_align_anchor_with_other_anchor(
    mock_gui: None,
    anchor1: PositionalAnchor,
    anchor2: PositionalAnchor,
    spacing: Union[int, Tuple[int, int], cocos.draw.Point2],
    expected_xy: Tuple[int, int],
) -> None:
    """Test aligning the anchor of one box with the anchor of another."""
    box1 = Box(BoxDefinition(width=1000, height=1000))
    box2 = Box(BoxDefinition(width=100, height=100))

    box2.align_anchor_with_other_anchor(
        box1, other_anchor=anchor1, self_anchor=anchor2, spacing=spacing
    )
    assert box2.position == expected_xy


def test_recreating_background(mock_gui):
    """Test that the background of a box can be recreated on definition change."""
    definition = BoxDefinition(background_color=White, width=1, height=1)
    box = Box(definition)

    assert box._background is not None
    assert box._background.color == White.as_tuple()

    definition2 = BoxDefinition(background_color=Black)

    box.definition = definition2
    box.update_background()
    assert box._background.color == Black.as_tuple()


def test_box_logging(mock_gui, caplog, subtests):
    """Test the custom logging handling for Box."""
    trace_marker = "__TRACE__"
    box = Box(BoxDefinition())

    # Set the initial log level to override the global level
    box.set_log_level(logging.DEBUG)

    # Send a log in to test
    box.debug("test1")
    last_log = caplog.records[-1]

    with subtests.test("No additional trace when trace logging is not enabled."):
        assert last_log.levelname == "DEBUG"
        assert trace_marker not in last_log.msg

    with subtests.test("Stack frame of log is from original logging location."):
        assert last_log.module == __name__.split(".")[-1]

    with subtests.test("Trace logs only generated when trace logging enabled."):
        box.set_log_level(logging.DEBUG)
        box.trace("test3")
        assert "test3" not in caplog.records[-1].msg

    box.enable_trace_logging()
    levels = {
        "TRACE": box.trace,
        "DEBUG": box.debug,
        "INFO": box.info,
        "WARNING": box.warning,
        "ERROR": box.error,
    }
    for level_name, log_fn in levels.items():
        with subtests.test(
            f"Trace information included in {level_name} logs when trace is enabled."
        ):
            log_fn("test2")
            last_log = caplog.records[-1]
            assert trace_marker in last_log.msg
            assert last_log.levelname == level_name
