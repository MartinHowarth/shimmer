import cocos
import pytest


from shimmer.display.data_structures import Color
from shimmer.display.components.box import Box
from shimmer.display.widgets.pop_up import (
    PopUpOnHover,
    PopUpToggleOnClick,
    PopUpWhileClicked,
)
from shimmer.display.components.box_track_cursor import BoxTrackCursor


def create_base_box():
    box = Box(cocos.rect.Rect(0, 0, 100, 100))
    box.background_color = Color(100, 20, 20)
    return box


def test_pop_up_on_hover(run_gui):
    """A pop up should appear when hovering over the button."""
    base_box = create_base_box()
    pop_up = Box(cocos.rect.Rect(200, 200, 200, 100))
    pop_up.background_color = Color(40, 40, 40)
    on_hover = PopUpOnHover(pop_up, base_box.rect)
    base_box.add(on_hover)
    assert run_gui(test_pop_up_on_hover, base_box)


def test_multiple_pop_ups_on_hover(run_gui):
    """Two pop ups should appear when hovering over the box."""
    base_box = create_base_box()
    pop_up = Box(cocos.rect.Rect(200, 200, 200, 100))
    pop_up.background_color = Color(40, 40, 40)
    pop_up2 = Box(cocos.rect.Rect(200, 0, 100, 100))
    pop_up2.background_color = Color(200, 100, 100)
    on_hover = PopUpOnHover(pop_up, base_box.rect)
    on_hover2 = PopUpOnHover(pop_up2, base_box.rect)
    base_box.add(on_hover)
    base_box.add(on_hover2)
    assert run_gui(test_multiple_pop_ups_on_hover, base_box)


def test_pop_up_on_hover_track_cursor(run_gui):
    """A pop up should appear when hovering over the box, and it should track the cursor."""
    base_box = create_base_box()
    pop_up = BoxTrackCursor(cocos.rect.Rect(0, 0, 200, 100), offset=(30, 10))
    pop_up.background_color = Color(40, 40, 40)
    on_hover = PopUpOnHover(pop_up, base_box.rect)
    base_box.add(on_hover)
    assert run_gui(test_pop_up_on_hover_track_cursor, base_box)


def test_pop_up_while_clicked(run_gui):
    """A pop up should appear while the button is pressed."""
    base_box = create_base_box()
    pop_up = Box(cocos.rect.Rect(100, 100, 200, 100))
    pop_up.background_color = Color(40, 40, 40)
    while_clicked = PopUpWhileClicked(pop_up, base_box.rect)
    base_box.add(while_clicked)
    assert run_gui(test_pop_up_while_clicked, base_box)


def test_pop_up_toggle_on_click(run_gui):
    """A pop up should appear when the box is pressed, and disappear when it is pressed again."""
    base_box = create_base_box()
    pop_up = Box(cocos.rect.Rect(100, 100, 200, 100))
    pop_up.background_color = Color(40, 40, 40)
    toggle_on_click = PopUpToggleOnClick(pop_up, base_box.rect)
    base_box.add(toggle_on_click)
    assert run_gui(test_pop_up_toggle_on_click, base_box)
