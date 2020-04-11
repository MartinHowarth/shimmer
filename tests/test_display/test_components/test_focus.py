"""Tests for the focus system."""

from typing import Tuple

import cocos
from shimmer.components.box import Box
from shimmer.components.focus import (
    FocusBox,
    VisualAndKeyboardFocusBox,
    _FocusStackHandler,
    FocusBoxDefinition,
)


def make_focus_box_pair() -> Tuple[
    VisualAndKeyboardFocusBox, VisualAndKeyboardFocusBox, Box, Box, _FocusStackHandler
]:
    """Create a pair of FocusBoxes with a common parent and stack handler."""
    stack = _FocusStackHandler()
    parent = Box()
    parent_parent = Box()
    parent_parent.add(parent)
    focus_box = VisualAndKeyboardFocusBox(FocusBoxDefinition(focus_stack=stack))
    focus_box2 = VisualAndKeyboardFocusBox(FocusBoxDefinition(focus_stack=stack))

    parent.add(focus_box)
    parent.add(focus_box2)

    focus_box.on_enter()
    focus_box2.on_enter()

    return focus_box, focus_box2, parent, parent_parent, stack


def test_focus_box_on_enter(mock_gui):
    """Test that a FocusBox registers itself with the stack handler on enter."""
    stack = _FocusStackHandler()
    parent = Box()
    focus_box = FocusBox(FocusBoxDefinition(focus_stack=stack))
    parent.add(focus_box, z=2)

    focus_box.on_enter()
    assert focus_box in stack._focus_stack


def test_focus_box_on_exit(mock_gui):
    """Test that a FocusBox de-registers itself with the stack handler on exit."""
    stack = _FocusStackHandler()
    parent = Box()
    focus_box = FocusBox(FocusBoxDefinition(focus_stack=stack))
    parent.add(focus_box)

    focus_box.on_enter()
    assert focus_box in stack._focus_stack
    focus_box.on_exit()
    assert focus_box not in stack._focus_stack


def test_focus_system_take_focus(subtests, mock_gui):
    """Test that FocusStack re-arranges the stack correctly when notified of a focus change."""
    focus_box, focus_box2, parent, parent_parent, stack = make_focus_box_pair()

    with subtests.test("Test focusing on one box when none are currently focused."):
        focus_box.take_focus()
        assert focus_box.is_focused is True
        assert focus_box2.is_focused is False
        assert stack._focus_stack == [focus_box, focus_box2]

    with subtests.test("Test focusing another box in the list."):
        focus_box2.take_focus()
        assert focus_box.is_focused is False
        assert focus_box2.is_focused is True
        assert stack._focus_stack == [focus_box2, focus_box]

    with subtests.test("Test no change when focusing the already focused box."):
        focus_box2.take_focus()
        assert focus_box.is_focused is False
        assert focus_box2.is_focused is True
        assert stack._focus_stack == [focus_box2, focus_box]


def test_focus_box_on_click(subtests, mock_gui, mock_mouse):
    """Test that a FocusBox takes focus when clicked on."""
    focus_box, focus_box2, parent, parent_parent, stack = make_focus_box_pair()

    with subtests.test("Test clicking when no box is focused."):
        mock_mouse.click(focus_box)
        assert focus_box.is_focused is True
        assert focus_box2.is_focused is False

    with subtests.test("Test clicking when that box is already focused."):
        mock_mouse.click(focus_box)
        assert focus_box.is_focused is True
        assert focus_box2.is_focused is False

    with subtests.test("Test clicking when another box is focused."):
        mock_mouse.click(focus_box2)
        assert focus_box.is_focused is False
        assert focus_box2.is_focused is True

    with subtests.test("Test click event is re-dispatched when focus is taken."):
        # Reset the mock received events.
        cocos.director.director.window.received_events = []
        mock_mouse.press(focus_box)
        received_events = cocos.director.director.window.received_events
        assert len(received_events) == 1
        assert received_events[0][0] == "on_mouse_press"

    with subtests.test(
        "Test click event is not re-dispatched when clicking an already focused box."
    ):
        # Reset the mock received events.
        cocos.director.director.window.received_events = []
        mock_mouse.press(focus_box)
        received_events = cocos.director.director.window.received_events
        assert len(received_events) == 0
