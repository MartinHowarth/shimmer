"""
Module defining a pop out menu for selecting multiple options in a concise way.

Also includes definitions for the following types of pop out menu:
  - Drop down menu
  - Pop up menu
  - Expand right menu
  - Expand left menu
"""
from dataclasses import dataclass, field, replace
from typing import Iterable, Callable, Dict, Optional

from .button import Button, ButtonDefinition, ToggleButton
from .scrollable_box import ScrollableBoxDefinition, ScrollableBox
from ..alignment import HorizontalAlignment
from ..alignment import RightTop, LeftTop, LeftBottom, PositionalAnchor
from ..components.box import Box, BoxDefinition
from ..components.box_layout import BoxColumn, BoxColumnDefinition
from ..components.mouse_box import MouseClickEventCallable, EVENT_HANDLED


@dataclass(frozen=True)
class PopOutMenuDefinition(BoxDefinition):
    """
    Definition of a menu which shows the menu choices when it is clicked on.

    The anchors define in which position the menu items are displayed relative to the menu button.

    :param menu_button_anchor: The anchor point of the menu button to use for alignment.
    :param item_layout_anchor: The anchor point of the menu item layout to align with the
        menu button anchor.
    :param name: The name to display on the menu button.
    :param items: List of Boxes to include in the menu.
    :param style: A ButtonDefinition to use as a base for the menu button.
    """

    menu_button_anchor: PositionalAnchor = LeftBottom
    item_layout_anchor: PositionalAnchor = LeftTop
    name: Optional[str] = None
    items: Iterable[Box] = field(default_factory=tuple)
    style: ButtonDefinition = ButtonDefinition()
    scrollable: bool = False
    scrollable_height: int = 200


@dataclass(frozen=True)
class DropDownMenuDefinition(PopOutMenuDefinition):
    """
    Definition of a pop out menu with the menu items configured to appear below the menu button.

    See `PopOutMenuDefinition` for parameter details.
    """

    menu_button_anchor: PositionalAnchor = LeftBottom
    item_layout_anchor: PositionalAnchor = LeftTop


@dataclass(frozen=True)
class PopUpMenuDefinition(PopOutMenuDefinition):
    """
    Definition of a pop out menu with the menu items configured to appear above the menu button.

    See `PopOutMenuDefinition` for parameter details.
    """

    menu_button_anchor: PositionalAnchor = LeftTop
    item_layout_anchor: PositionalAnchor = LeftBottom


@dataclass(frozen=True)
class ExpandRightMenuDefinition(PopOutMenuDefinition):
    """
    Definition of a pop out menu with the menu items configured to appear on the right.

    See `PopOutMenuDefinition` for parameter details.
    """

    menu_button_anchor: PositionalAnchor = RightTop
    item_layout_anchor: PositionalAnchor = LeftTop


@dataclass(frozen=True)
class ExpandLeftMenuDefinition(PopOutMenuDefinition):
    """
    Definition of a pop out menu with the menu items configured to appear on the left.

    See `PopOutMenuDefinition` for parameter details.
    """

    menu_button_anchor: PositionalAnchor = LeftTop
    item_layout_anchor: PositionalAnchor = RightTop


class PopOutMenu(Box):
    """
    A menu for selecting multiple options where the options appear when the menu is clicked on.

    This is a widget consisting of a toggle button of the menu header and a set of buttons
    for each option in the menu.

    For example, this is used to create a Drop-Down menu or a Pop-Up menu.
    """

    def __init__(self, definition: PopOutMenuDefinition):
        """Create a new PopOutMenu."""
        super(PopOutMenu, self).__init__(definition)
        self.definition: PopOutMenuDefinition = self.definition
        self._expanded: bool = False
        self.scrollable_box: Optional[ScrollableBox] = None

        self.menu_button = ToggleButton(self.get_menu_button_definition())
        self.item_layout = BoxColumn(
            BoxColumnDefinition(spacing=0, alignment=HorizontalAlignment.left),
            boxes=self.definition.items,
        )
        # Add the menu button with a high z value to appear above the children and receive
        # events first.
        self.add(self.menu_button)

        # Do not add the item_layout/scrollable_box now so it is not visible initially.
        # Add/remove it when expanding/collapsing the menu.
        if self.definition.scrollable:
            self.scrollable_box = ScrollableBox(
                ScrollableBoxDefinition(
                    height=self.definition.scrollable_height,
                    width=self.item_layout.rect.width,
                )
            )
            self.scrollable_box.add(self.item_layout)
            # Align with top-left. This is needed if the size of the item layout is smaller
            # than `self.definition.scrollable_height` otherwise a gap appears between the menu
            # button and the actual items.
            self.item_layout.align_anchor_with_other_anchor(
                self.scrollable_box.view_port_box, LeftTop
            )
            # Start with the slider at the top.
            self.scrollable_box.vertical_scrollbar.value = (
                self.scrollable_box.definition.slider_definition.maximum
            )
        #     child = self.scrollable_box
        # else:
        #     child = self.item_layout
        # child.align_anchor_with_other_anchor(
        #     self.menu_button,
        #     self.definition.menu_button_anchor,
        #     self.definition.item_layout_anchor,
        # )
        self.arrange_children()
        # self.add(child)
        # self._hide_items()

    def arrange_children(self):
        if self.scrollable_box is not None:
            child = self.scrollable_box
        else:
            child = self.item_layout
        child.align_anchor_with_other_anchor(
            self.menu_button,
            self.definition.menu_button_anchor,
            self.definition.item_layout_anchor,
        )

    #
    # def disable(self):
    #     super(PopOutMenu, self).disable()
    #     self.menu_button.disable()
    #     self._hide_items()
    #
    # def enable(self):
    #     super(PopOutMenu, self).enable()
    #     self.menu_button.enable()

    def get_menu_button_definition(self) -> ButtonDefinition:
        """Build the ButtonDefinition to use for the main menu button."""
        return replace(
            self.definition.style,
            text=self.definition.name,
            on_press=self.expand_menu,
            on_release=self.collapse_menu,
            # Collapse the menu on a press outside of the menu.
            # The menu items are added after so will have the opportunity to consume the
            # mouse event first.
            on_press_outside=self.on_click_outside,
        )

    def expand_menu(self, *_, **__):
        """Expand the drop down menu."""
        if self._expanded is False:
            self.debug(f"Expanding pop out menu.")
            self._expanded = True
            if self.scrollable_box is not None:
                child = self.scrollable_box
            else:
                child = self.item_layout
            self.add(child)
            self.arrange_children()
            self.debug(f"{self.menu_button.position=}")
            self.debug(f"{self.menu_button.rect=}")
            self.debug(f"{child.position=}")
            self.debug(f"{child.world_rect=}")
            self.debug(f"{child.view_port_box.position=}")
            self.debug(f"{child.view_port_box.world_rect=}")
            self.debug(f"{child.view_port_box.viewport.position=}")
            self.debug(f"{child.view_port_box.viewport.world_rect=}")
            self.debug(f"{child.world_rect=}")
            self.debug(f"{child.vertical_scrollbar.world_rect=}")
        return EVENT_HANDLED

    def collapse_menu(self, *_, **__):
        """Collapse the drop down menu."""
        if self._expanded is True:
            self.debug(f"Collapsing pop out menu.")
            self._expanded = False
            if self.scrollable_box is not None:
                child = self.scrollable_box
            else:
                child = self.item_layout
            self.remove(child)
        return EVENT_HANDLED

    def on_click_outside(self, *_, **__):
        """
        Close the menu when a click occurs outside of the menu.

        This relies on the menu items being higher up the event stack so they receive
        mouse events before the menu button receives the click event outside of itself.
        """
        # By toggling the menu button off, `collapse_menu` will get called as the closing
        # action.
        self.menu_button.is_toggled = False

    # def _calculate_current_size(self) -> None:
    #     """
    #     Get the bounding rect of this PopOutMenu.
    #
    #     This is just the main menu button of the drop down. It does not include the actual
    #     items when expanded. This is because a PopOutMenu is typically positioned based on
    #     the size of the menu button, and not the possible size when expanded.
    #     """
    #     menu_rect = self.menu_button.rect
    #     self._width = menu_rect.width
    #     self._height = menu_rect.height


def construct_pop_out_menu_from_callables(
    definition: PopOutMenuDefinition, callable_dict: Dict[str, Callable[[], None]],
) -> PopOutMenu:
    """
    Create a pop out menu with one button for each callable in the given dictionary.

    :param definition: The definition of the pop out menu. The `items` parameter will be ignored
        and filled in by this function.
        The style in the definition will be used for all items and the menu button itself.
    :param callable_dict: Dictionary of the menu items to display, mapping the name of the item
        to the callback to call when it is selected.
        The order of items in the dict is the order in which the menu items will be displayed.
    """

    def ignore_arguments_callback(func: Callable[[], None]) -> MouseClickEventCallable:
        def inner(*_, **__):
            return func()

        return inner

    item_buttons = []
    for name, callback in callable_dict.items():
        button_definition = replace(
            definition.style, text=name, on_press=ignore_arguments_callback(callback)
        )
        item_buttons.append(Button(button_definition))

    definition = replace(definition, items=item_buttons)
    menu = PopOutMenu(definition)
    return menu
