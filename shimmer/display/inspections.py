"""Collection of methods for inspecting the GUI state."""

import cocos

from typing import Type, List, Iterable, Generator, Optional

from .components.box import Box


def get_all_nodes_of_type(
    _type: Type[cocos.cocosnode.CocosNode], scene: Optional[cocos.scene.Scene] = None
) -> List[cocos.cocosnode.CocosNode]:
    """
    Discover all nodes in the current cocos Scene that match the given type.

    :param _type: Type to match on, e.g. `Box`.
    :param scene: The cocos Scene to inspect.
        If None, defaults to the current Scene.
    :return: List of matching nodes.
    """

    def matching_type(node: cocos.cocosnode.CocosNode) -> cocos.cocosnode.CocosNode:
        nonlocal _type
        if isinstance(node, _type):
            return node

    if scene is None:
        scene = cocos.director.director.scene

    return scene.walk(matching_type)


def get_boxes_that_intersect_with_rect(
    boxes: Iterable[Box], rect: cocos.rect.Rect
) -> Generator[Box, None, None]:
    """
    Find which of the given boxes intersect with the given rect.

    Intersection is determined in world coordinate space.

    :param boxes: List of boxes to check.
    :param rect: Rect to check intersection with.
    :return: Generator of boxes that intersect with `rect`.
    """
    for test_box in boxes:
        if test_box.world_rect.intersects(rect):
            yield test_box


def get_boxes_that_intersect_with_box(
    boxes: Iterable[Box], box: Box
) -> Generator[Box, None, None]:
    """
    Find which of the given boxes intersect with the given Box.

    Intersection is determined in world coordinate space.

    :param boxes: List of boxes to check.
    :param box: Box to check intersection with.
    :return: Generator of boxes that intersect with `box`.
    """
    yield from get_boxes_that_intersect_with_rect(boxes, box.world_rect)
