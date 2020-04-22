"""Tests for ViewPortBox."""

from shimmer.components.box import DynamicSizeBehaviourEnum, BoxDefinition, Box
from shimmer.components.draggable_box import (
    DragParentBox,
    DraggableBoxDefinition,
)
from shimmer.components.sprite_box import SpriteBox, SpriteBoxDefinition
from shimmer.components.view_port_box import ViewPortBox
from shimmer.widgets.button import Button, ButtonDefinition


def test_view_port_box(run_gui, cat_image):
    """A viewport onto a kitten picture should be draggable."""
    cat = SpriteBox(SpriteBoxDefinition(width=400, height=400, image=cat_image))
    # Create the viewport manager and add the cat sprite to it to provide
    # something to be seen.
    view_port = ViewPortBox(BoxDefinition(width=100, height=100))
    view_port.add(cat)

    # Make the actual viewable area draggable.
    drag_box = DragParentBox(
        DraggableBoxDefinition(
            dynamic_size_behaviour=DynamicSizeBehaviourEnum.match_parent
        )
    )
    view_port.add_to_viewport(drag_box)

    assert run_gui(test_view_port_box, view_port)


def test_view_port_box_no_click_through(run_gui, cat_image):
    """
    A viewport onto a button should be shown.

    The button only highlight when the mouse moves inside the viewport and not when
    the mouse is outside of the viewport.
    """
    button = Button(ButtonDefinition(width=400, height=400))

    view_port = ViewPortBox(BoxDefinition(width=100, height=100))
    view_port.add(button)

    # Make the actual viewable area draggable.
    drag_box = DragParentBox(
        DraggableBoxDefinition(
            dynamic_size_behaviour=DynamicSizeBehaviourEnum.match_parent
        )
    )
    view_port.add_to_viewport(drag_box)

    assert run_gui(test_view_port_box, view_port)


def test_viewport_box_is_visible(mock_gui, subtests):
    """Test the `box_is_visible` method of the ViewPortBox."""
    box = Box(BoxDefinition(width=100, height=100))
    view_port = ViewPortBox(BoxDefinition(width=10, height=10))
    view_port.add(box)

    with subtests.test("Initial overlap (position = (0, 0)) means box is visible."):
        assert view_port.box_is_visible(box) is True

    with subtests.test("Partial overlap means box is visible."):
        # Move the actual viewport, not the ViewPortBox
        view_port.viewport.position = (95, 95)
        assert view_port.box_is_visible(box) is True

    with subtests.test("No overlap means box is not visible."):
        # Move the actual viewport, not the ViewPortBox
        view_port.viewport.position = (300, 300)
        assert view_port.box_is_visible(box) is False


# TODO add tests for dynamic size of view port parent etc.
