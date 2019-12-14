import cocos

from shimmer.display.components.box import Box
from shimmer.display.components.draggable_anchor import DraggableAnchor
from shimmer.display.data_structures import Color


def create_base_box():
    box = Box(cocos.rect.Rect(0, 0, 100, 100))
    box.background_color = Color(100, 20, 20)
    return box


def test_draggable_anchor(run_gui):
    """The box should be a draggable."""
    base_box = create_base_box()
    anchor = DraggableAnchor(base_box.rect)

    base_box.add(anchor)

    assert run_gui(test_draggable_anchor, base_box)
