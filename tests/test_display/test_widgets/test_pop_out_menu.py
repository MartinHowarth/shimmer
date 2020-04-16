"""Tests for the pop out menu."""

from typing import List, Callable

import pytest

from shimmer.widgets.pop_out_menu import (
    PopOutMenu,
    PopUpMenuDefinition,
    ExpandLeftMenuDefinition,
    ExpandRightMenuDefinition,
    DropDownMenuDefinition,
    Button,
    ButtonDefinition,
)


def create_simple_menu_items(
    callback: Callable[[str], Callable], num_items: int
) -> List[Button]:
    """Create a set of menu items that call the given callback with their index."""
    menu_items = [
        Button(ButtonDefinition(text=str(i), on_press=callback(str(i)), width=200,))
        for i in range(num_items)
    ]
    return menu_items


@pytest.fixture
def pop_out_menu_items(updatable_text_box):
    """Fixture providing a list of buttons that update a text box with their label."""
    text_box, update_text_box = updatable_text_box

    def update_text_callback(new_text):
        def mouse_event(*_, **__):
            update_text_box(new_text)

        return mouse_event

    menu_items = create_simple_menu_items(update_text_callback, 5)
    return menu_items, text_box


def test_drop_down_menu_user(run_gui, pop_out_menu_items):
    """A drop down menu should be shown and interactable."""
    menu_items, text_box = pop_out_menu_items

    menu = PopOutMenu(
        DropDownMenuDefinition(name="Choose an integer", items=menu_items)
    )
    # Ensure the menu has enough space to be seen when expanded.
    menu.position = (
        0,
        200,
    )

    assert run_gui(test_drop_down_menu_user, text_box, menu)


def test_pop_out_menu(mock_gui, subtests, mock_mouse, pop_out_menu_items):
    """Test that the menu items appear/disappear when the menu is toggled."""
    menu_items, text_box = pop_out_menu_items

    menu = PopOutMenu(
        DropDownMenuDefinition(name="Choose an integer", items=menu_items)
    )
    with subtests.test("Test that menu items are not in the scene initially."):
        assert menu.item_layout not in menu.get_children()

    with subtests.test("Test that menu items are added when the menu is clicked."):
        mock_mouse.click(menu.menu_button)
        assert menu.item_layout in menu.get_children()

    with subtests.test(
        "Test that menu items are removed when the menu is clicked a second time."
    ):
        mock_mouse.click(menu.menu_button)
        assert menu.item_layout not in menu.get_children()

    with subtests.test(
        "Test that menu items are removed when a click occurs off the menu."
    ):
        # First expand the menu
        mock_mouse.click(menu.menu_button)
        assert menu.item_layout in menu.get_children()
        # Then click outside it to trigger it to close.
        mock_mouse.press(menu.menu_button, position=(1000, 1000))
        assert menu.item_layout not in menu.get_children()


def test_drop_down_menu(mock_gui, pop_out_menu_items):
    """Test that the positioning of DropDownMenu is correct."""
    menu_items, text_box = pop_out_menu_items

    menu = PopOutMenu(
        DropDownMenuDefinition(name="Choose an integer", items=menu_items)
    )
    menu.menu_button.is_toggled = True
    assert menu.item_layout.x == menu.menu_button.x
    assert menu.item_layout.y == -menu.item_layout.rect.height


def test_pop_up_menu(mock_gui, pop_out_menu_items):
    """Test that the positioning of PopUpMenu is correct."""
    menu_items, text_box = pop_out_menu_items

    menu = PopOutMenu(PopUpMenuDefinition(name="Choose an integer", items=menu_items))
    menu.menu_button.is_toggled = True
    assert menu.item_layout.x == menu.menu_button.x
    assert menu.item_layout.y == menu.menu_button.rect.height


def test_expand_right_menu(mock_gui, pop_out_menu_items):
    """Test that the positioning of ExpandRightMenu is correct."""
    menu_items, text_box = pop_out_menu_items

    menu = PopOutMenu(
        ExpandRightMenuDefinition(name="Choose an integer", items=menu_items)
    )
    menu.menu_button.is_toggled = True
    assert menu.item_layout.x == menu.menu_button.rect.width
    assert (
        menu.item_layout.y
        == menu.menu_button.rect.height - menu.item_layout.rect.height
    )


def test_expand_left_menu(mock_gui, pop_out_menu_items):
    """Test that the positioning of ExpandLeftMenu is correct."""
    menu_items, text_box = pop_out_menu_items

    menu = PopOutMenu(
        ExpandLeftMenuDefinition(name="Choose an integer", items=menu_items)
    )
    menu.menu_button.is_toggled = True
    assert menu.item_layout.x == -menu.item_layout.rect.width
    assert (
        menu.item_layout.y
        == menu.menu_button.rect.height - menu.item_layout.rect.height
    )


def test_nested_pop_out_menu(run_gui, pop_out_menu_items):
    """A tree of pop-out menus should be shown and interactable."""
    menu_items, text_box = pop_out_menu_items

    def update_text_callback(new_text):
        def mouse_event(*_, **__):
            text_box.set_text(new_text)

        return mouse_event

    sub_menus = [
        PopOutMenu(
            ExpandRightMenuDefinition(
                name="Choose an integer",
                items=create_simple_menu_items(update_text_callback, 3),
            )
        )
        for _ in range(3)
    ]
    top_menu = PopOutMenu(DropDownMenuDefinition(name="Click me!", items=sub_menus))
    # Ensure the menu has enough space to be seen when expanded.
    top_menu.position = (
        0,
        200,
    )

    assert run_gui(test_nested_pop_out_menu, text_box, top_menu)
