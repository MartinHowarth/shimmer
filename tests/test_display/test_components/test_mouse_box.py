"""
Tests for the MouseBox component.

Performs tests with a mock GUI to check event handling is correct.
"""

from dataclasses import replace
from typing import no_type_check

from mock import MagicMock

from shimmer.components.mouse_box import MouseBox, MouseBoxDefinition


@no_type_check  # Ignore typing because Mocks don't type nicely.
def test_all_callbacks_can_be_called(subtests, mock_gui, mock_mouse):
    """
    Test that all callbacks can be called, except drag.

    Drag is handled in another test as it's more complicated.

    Also test that they consume the events when they return True.
    """
    definition = MouseBoxDefinition(
        width=100,
        height=100,
        on_press=MagicMock(return_value=True),
        on_release=MagicMock(return_value=True),
        on_hover=MagicMock(return_value=True),
        on_unhover=MagicMock(return_value=True),
        on_motion=MagicMock(return_value=True),
        on_drag=MagicMock(return_value=True),
    )
    box = MouseBox(definition)
    # Set position to non-origin to make the test more realistic / interesting.
    box.position = 100, 100

    with subtests.test("Test on_select callback."):
        handled = mock_mouse.press(box)
        assert handled is True
        definition.on_press.assert_called_once()

    with subtests.test("Test on_release callback."):
        handled = mock_mouse.release(box)
        assert handled is True
        definition.on_release.assert_called_once()

    with subtests.test("Test on_hover, on_motion and and on_unhover callback."):
        # Bundled three events together because order is important here.
        handled = mock_mouse.move_onto(box)
        assert handled is True
        definition.on_hover.assert_called_once()

        # Very small motion within the box.
        handled = mock_mouse.move(box)
        assert handled is True
        definition.on_motion.assert_called_once()

        handled = mock_mouse.move_off(box)
        assert handled is True
        definition.on_unhover.assert_called_once()


@no_type_check  # Ignore typing because Mocks don't type nicely.
def test_drag_callback_can_be_called(subtests, mock_gui, mock_mouse):
    """
    Test that the drag callback can be called.

    Also test that they consume the events when they return True.
    """
    definition = MouseBoxDefinition(
        width=100,
        height=100,
        on_press=MagicMock(return_value=True),
        on_release=MagicMock(return_value=True),
        on_hover=MagicMock(return_value=True),
        on_unhover=MagicMock(return_value=True),
        on_motion=MagicMock(return_value=True),
        on_drag=MagicMock(return_value=True),
    )
    box = MouseBox(definition)
    box.position = 100, 100
    box.definition = replace(
        box.definition, on_press=box.start_dragging, on_release=box.stop_dragging
    )

    mock_mouse.click_and_drag(box, (110, 110), (120, 120))
    definition.on_hover.assert_not_called()
    definition.on_unhover.assert_not_called()
    definition.on_motion.assert_not_called()
    definition.on_drag.assert_called_once()


@no_type_check  # Ignore typing because Mocks don't type nicely.
def test_should_handle_coord(mock_gui, mock_mouse, subtests):
    """Test that `additional_coord_check_fn` impacts whether a mouse event should be handled."""
    definition = MouseBoxDefinition(
        width=100, height=100, on_press=MagicMock(return_value=True),
    )
    box = MouseBox(definition)

    with subtests.test(
        f"additional_coord_check_fn returns False should not call callback."
    ):
        box.additional_coord_check_fn = lambda x, y: False
        mock_mouse.click(box)
        definition.on_press.assert_not_called()

    with subtests.test(f"additional_coord_check_fn returns True should call callback."):
        box.additional_coord_check_fn = lambda x, y: True
        mock_mouse.click(box)
        definition.on_press.assert_called_once()
