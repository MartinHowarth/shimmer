"""Test pop_up method definitions."""

import cocos

from shimmer.display.data_structures import Color
from shimmer.display.components.box import Box
from shimmer.display.components.mouse_box import (
    MouseBox,
    MouseBoxDefinition,
)
from shimmer.display.helpers import bundle_callables
from shimmer.display.components.pop_up import (
    create_pop_up_later,
    remove_pop_up_later,
    toggle_pop_up_later,
)
from shimmer.display.components.box_track_cursor import BoxTrackCursor


def create_mouse_box(definition: MouseBoxDefinition) -> MouseBox:
    """Create a MouseBox with a background color and the given defintion."""
    box = MouseBox(definition, cocos.rect.Rect(0, 0, 100, 100))
    box.background_color = Color(100, 20, 20)
    return box


def test_pop_up_on_hover(run_gui):
    """A pop up should appear when hovering over the button."""
    pop_up = Box(cocos.rect.Rect(200, 200, 200, 100))
    pop_up.background_color = Color(40, 40, 40)
    base_box = create_mouse_box(
        MouseBoxDefinition(
            on_hover=create_pop_up_later(pop_up),
            on_unhover=remove_pop_up_later(pop_up),
        )
    )
    assert run_gui(test_pop_up_on_hover, base_box)


def test_multiple_pop_ups_on_hover(run_gui):
    """Two pop ups should appear when hovering over the box."""
    pop_up = Box(cocos.rect.Rect(200, 200, 200, 100))
    pop_up.background_color = Color(40, 40, 40)
    pop_up2 = Box(cocos.rect.Rect(200, 0, 100, 100))
    pop_up2.background_color = Color(200, 100, 100)

    create_two_pop_ups = bundle_callables(
        create_pop_up_later(pop_up), create_pop_up_later(pop_up2)
    )
    remove_two_pop_ups = bundle_callables(
        remove_pop_up_later(pop_up), remove_pop_up_later(pop_up2)
    )

    base_box_defn = MouseBoxDefinition(
        on_hover=create_two_pop_ups, on_unhover=remove_two_pop_ups,
    )

    base_box = create_mouse_box(base_box_defn)

    assert run_gui(test_multiple_pop_ups_on_hover, base_box)


def test_pop_up_on_hover_track_cursor(run_gui):
    """A pop up should appear when hovering over the box, and it should track the cursor."""
    pop_up = BoxTrackCursor(cocos.rect.Rect(0, 0, 200, 100), offset=(30, 10))
    pop_up.background_color = Color(40, 40, 40)
    base_box = create_mouse_box(
        MouseBoxDefinition(
            on_hover=create_pop_up_later(pop_up),
            on_unhover=remove_pop_up_later(pop_up),
        )
    )
    assert run_gui(test_pop_up_on_hover_track_cursor, base_box)


def test_pop_up_while_clicked(run_gui):
    """A pop up should appear while the button is pressed."""
    pop_up = Box(cocos.rect.Rect(100, 100, 200, 100))
    pop_up.background_color = Color(40, 40, 40)
    base_box = create_mouse_box(
        MouseBoxDefinition(
            on_press=create_pop_up_later(pop_up),
            on_release=remove_pop_up_later(pop_up),
        )
    )
    assert run_gui(test_pop_up_while_clicked, base_box)


def test_pop_up_toggle_on_click(run_gui):
    """A pop up should appear when the box is pressed, and disappear when it is pressed again."""
    pop_up = Box(cocos.rect.Rect(100, 100, 200, 100))
    pop_up.background_color = Color(40, 40, 40)

    base_box = create_mouse_box(
        MouseBoxDefinition(on_press=toggle_pop_up_later(pop_up),)
    )
    assert run_gui(test_pop_up_toggle_on_click, base_box)
