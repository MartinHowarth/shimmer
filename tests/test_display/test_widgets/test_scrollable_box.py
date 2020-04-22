"""Tests for the ScrollableBox widget."""

from shimmer.components.box import Box, BoxDefinition
from shimmer.components.sprite_box import SpriteBoxDefinition, SpriteBox
from shimmer.widgets.scrollable_box import ScrollableBox, ScrollableBoxDefinition
from shimmer.widgets.slider import SliderDefinition


def test_scrollable_box_with_gui(run_gui, cat_image, null_slider_text_definition):
    """A view port should be shown onto an image of a cat with scrollbars to move the view."""
    cat = SpriteBox(SpriteBoxDefinition(image=cat_image))
    scrollable_box = ScrollableBox(
        ScrollableBoxDefinition(
            width=400,
            height=200,
            vertically_scrollable=True,
            horizontally_scrollable=True,
            slider_definition=SliderDefinition(
                button_text_definition=null_slider_text_definition, width=40, height=40
            ),
        )
    )
    scrollable_box.add(cat)

    assert run_gui(test_scrollable_box_with_gui, scrollable_box)


def test_scrollable_box_vertical_only(
    mock_gui, cat_image, subtests, null_slider_text_definition
):
    """
    Test the positions of all important sub boxes of the ScrollableBox.

    This test covers the case when the box is only scrollable vertically.
    """
    child_box = Box(BoxDefinition(width=400, height=800))
    scrollable_box = ScrollableBox(
        ScrollableBoxDefinition(
            width=400,
            height=200,
            vertically_scrollable=True,
            horizontally_scrollable=False,
            slider_definition=SliderDefinition(
                button_text_definition=null_slider_text_definition, width=40
            ),
        )
    )
    scrollable_box.add(child_box)

    with subtests.test(f"Test that initial position is as expected."):
        assert scrollable_box.position == (0, 0)
        assert scrollable_box.view_port_box.position == (0, 0)
        assert scrollable_box.view_port_box.viewport.position == (0, 0)
        assert child_box.position == (0, 0)

    with subtests.test(f"Test that scrolling up once results in correct box movement."):
        scrollable_box.vertical_scrollbar.increment(0.5)

        # Scrollable box itself should not move.
        assert scrollable_box.position == (0, 0)
        # Obscured children should not move
        assert child_box.position == (0, 0)
        # View port box should move down.
        assert scrollable_box.view_port_box.position == (0, -300)
        # Actual view port should move up.
        assert scrollable_box.view_port_box.viewport.position == (0, 300)

    with subtests.test(f"Test that scrolling down results in correct box movement."):
        scrollable_box.vertical_scrollbar.decrement(0.1)

        # Scrollable box itself should not move.
        assert scrollable_box.position == (0, 0)
        # Obscured children should not move
        assert child_box.position == (0, 0)
        # View port box should move down.
        assert scrollable_box.view_port_box.position == (0, -240)
        # Actual view port should move up.
        assert scrollable_box.view_port_box.viewport.position == (0, 240)


def test_scrollable_box_both_directions(
    mock_gui, cat_image, subtests, null_slider_text_definition
):
    """
    Test the positions of all important sub boxes of the ScrollableBox.

    This test covers the case when the box is scrollable in both directions.
    This is interesting because the horizontal scrollbar appears at the bottom so
    positioning of boxes is offset by a different amount in the vertical direction
    when it is included.
    """
    scrollbar_width = 40
    child_box = Box(BoxDefinition(width=800, height=800))
    scrollable_box = ScrollableBox(
        ScrollableBoxDefinition(
            width=400,
            height=200,
            vertically_scrollable=True,
            horizontally_scrollable=True,
            slider_definition=SliderDefinition(
                button_text_definition=null_slider_text_definition,
                width=scrollbar_width,
                height=scrollbar_width,
            ),
        )
    )
    scrollable_box.add(child_box)

    with subtests.test(f"Test that initial position is as expected."):
        assert scrollable_box.position == (0, 0)
        assert scrollable_box.view_port_box.position == (0, scrollbar_width)
        assert scrollable_box.view_port_box.viewport.position == (0, 0)
        assert child_box.position == (0, 0)

    with subtests.test(f"Test that scrolling up once results in correct box movement."):
        scrollable_box.vertical_scrollbar.increment(0.5)

        # Scrollable box itself should not move.
        assert scrollable_box.position == (0, 0)
        # Obscured children should not move
        assert child_box.position == (0, 0)
        # View port box should move down.
        assert scrollable_box.view_port_box.position == (0, -280)
        # Actual view port should move up.
        assert scrollable_box.view_port_box.viewport.position == (0, 320)

    with subtests.test(f"Test that scrolling down results in correct box movement."):
        scrollable_box.vertical_scrollbar.decrement(0.1)

        # Scrollable box itself should not move.
        assert scrollable_box.position == (0, 0)
        # Obscured children should not move
        assert child_box.position == (0, 0)
        # View port box should move down.
        assert scrollable_box.view_port_box.position == (0, -216)
        # Actual view port should move up.
        assert scrollable_box.view_port_box.viewport.position == (0, 256)

    with subtests.test(
        f"Test that scrolling right once results in correct box movement."
    ):
        scrollable_box.horizontal_scrollbar.increment(0.5)

        # Scrollable box itself should not move.
        assert scrollable_box.position == (0, 0)
        # Obscured children should not move
        assert child_box.position == (0, 0)
        # View port box should move down.
        assert scrollable_box.view_port_box.position == (-220, -216)
        # Actual view port should move up.
        assert scrollable_box.view_port_box.viewport.position == (220, 256)

    with subtests.test(f"Test that scrolling left results in correct box movement."):
        scrollable_box.horizontal_scrollbar.decrement(0.1)

        # Scrollable box itself should not move.
        assert scrollable_box.position == (0, 0)
        # Obscured children should not move
        assert child_box.position == (0, 0)
        # View port box should move down.
        assert scrollable_box.view_port_box.position == (-176, -216)
        # Actual view port should move up.
        assert scrollable_box.view_port_box.viewport.position == (176, 256)
