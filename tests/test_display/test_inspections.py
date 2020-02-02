"""Tests for methods that inspect the current GUI state."""

import cocos

from shimmer.display.components.box import Box, BoxDefinition
from shimmer.display.inspections import (
    get_boxes_that_intersect_with_box,
    get_all_nodes_of_type,
)


def test_get_all_nodes_of_type(run_gui, subtests):
    """Test that get_all_nodes_of_type filters nodes correctly."""
    # `run_gui` isn't needed for the display, but it must be initialised to be able to
    # create any cocos nodes.

    # Run this test with a custom scene because the global scene may have random extra
    # stuff added to it.
    scene = cocos.scene.Scene()
    box1, box2 = Box(), Box()
    node = cocos.cocosnode.CocosNode()
    scene.add(node)
    scene.add(box1)
    scene.add(box2)

    with subtests.test("All subclasses should also get included."):
        # Boxes and Scene are subclasses of CocosNode, so should include:
        # - box1, box2, node, scene
        nodes = get_all_nodes_of_type(cocos.cocosnode.CocosNode, scene)
        assert len(nodes) == 4
        assert all([x in nodes for x in [box1, box2, node, scene]])

    with subtests.test("Only specific subclass should get included."):
        nodes = get_all_nodes_of_type(Box, scene)
        assert len(nodes) == 2
        assert all([x in nodes for x in [box1, box2]])


def test_get_boxes_that_intersect_with(run_gui, subtests):
    """Test that get_boxes_that_intersect_with filters nodes correctly."""
    # `run_gui` isn't needed for the display, but it must be initialised to be able to
    # create any cocos nodes.

    box1 = Box(BoxDefinition(10, 10))
    box2 = Box(BoxDefinition(10, 10))
    box2.position = 100, 100
    boxes = [box1, box2]

    with subtests.test("Test partial overlap with single box."):
        test_box = Box(BoxDefinition(5, 5))
        overlap = list(get_boxes_that_intersect_with_box(boxes, test_box))
        assert len(overlap) == 1
        assert box1 in overlap

    with subtests.test("Test single overlap with box not near the origin."):
        test_box = Box(BoxDefinition(20, 20))
        test_box.position = 90, 90
        overlap = list(get_boxes_that_intersect_with_box(boxes, test_box))
        assert len(overlap) == 1
        assert box2 in overlap

    with subtests.test("Test overlap with multiple boxes."):
        test_box = Box(BoxDefinition(200, 200))
        overlap = list(get_boxes_that_intersect_with_box(boxes, test_box))
        assert len(overlap) == 2
        assert box1 in overlap
        assert box2 in overlap
