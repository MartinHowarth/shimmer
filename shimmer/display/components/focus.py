"""
Module defining nodes which can be focused.

A focused node:
  - consumes all mouse events within its area, preventing underlying nodes from receiving them.
  - gets first priority on keyboard event handling.

A common example of focus is handling overlapping windows - one appears on top of the other
and consumes all mouse events, preventing the one underneath from being accidentally interacted
with.
"""

import logging
from dataclasses import dataclass, replace, field
from typing import List, Optional, Callable, Type, cast

import cocos
from .box import Box
from .mouse_box import (
    MouseBox,
    MouseBoxDefinition,
    EVENT_HANDLED,
    EVENT_UNHANDLED,
)
from ..alignment import ZIndexEnum
from ..keyboard import KeyboardHandler

log = logging.getLogger(__name__)


class _FocusStackHandler:
    """
    Stack of FocusBoxes to record the order in which FocusBoxes have been focused.

    This enables behaviour such as:
      - When one window is closed, the one that was focused last gets focused again.

    The global singleton `FocusStackHandler` is available for use as the default focus stack.
    """

    def __init__(self):
        """
        Create a new FocusStackHandler.

        Typically to be used as a singleton.
        """
        self._focus_stack: List[FocusBox] = []

    @property
    def current_focus(self) -> Optional["FocusBox"]:
        """
        Return the currently focused FocusBox.

        If there is no current focus, return None.
        """
        if not self._focus_stack:
            return None

        # Top of the stack should be the only one that could be focused.
        # However, it could also not be currently focused, so test for that.
        top = self._focus_stack[0]
        if top.is_focused:
            return top
        return None

    def register_focus_box(self, focus_box: "FocusBox") -> None:
        """
        Add the given focus box to the end of the focus stack.

        :param focus_box: FocusBox to add to the stack.
        """
        self._focus_stack.append(focus_box)

    def unregister_focus_box(self, focus_box: "FocusBox") -> None:
        """
        Remove the given focus box from the stack and remove focus from it.

        :param focus_box: FocusBox to remove from the stack.
        """
        try:
            self._focus_stack.remove(focus_box)
        except ValueError:
            # FocusBox not in stack, nothing to do. This should never happen
            pass

    def notify_focused(self, focus_box: "FocusBox") -> None:
        """
        Move the given box to the top of the focus stack.

        Set all other boxes in the stack as unfocused.

        :param focus_box: The box that has been focused.
        """
        self._focus_stack.remove(focus_box)
        self._focus_stack.insert(0, focus_box)

        for box in self._focus_stack[1:]:
            log.debug(f"{box} told to lose focus, due to {focus_box}.")
            box.lose_focus()

    def focus_highest_in_stack(self) -> Optional["FocusBox"]:
        """
        Give focus to the highest box in the stack.

        :return: The box that has been focused.
        """
        if len(self._focus_stack) > 0:
            self._focus_stack[0].take_focus()
            return self._focus_stack[0]
        return None

    def __str__(self):
        """String representation of a FocusStackHandler."""
        if self is FocusStackHandler:
            return "GlobalFocusStackHandler"
        return super(_FocusStackHandler, self).__str__()


# The global focus stack.
FocusStackHandler = _FocusStackHandler()


@dataclass(frozen=True)
class FocusBoxDefinition(MouseBoxDefinition):
    """
    Definition of a FocusBox.

    :param on_take_focus: Called when the FocusBox gains focus.
    :param on_lose_focus: Called when the FocusBox loses focus.
    :param focus_stack: The focus stack to use. Defaults to the global singleton.
    """

    on_take_focus: Optional[Callable[[], None]] = None
    on_lose_focus: Optional[Callable[[], None]] = None
    focus_stack: _FocusStackHandler = field(default=FocusStackHandler)


class FocusBox(MouseBox):
    """A mouse box that when clicked causes its parent to take focus."""

    def __init__(self, definition: FocusBoxDefinition):
        """
        Create a new FocusBox.

        Registers this FocusBox with the focus stack handler.

        :param definition: BoxDefinition defining the shape of the focus box.
        """
        definition = replace(
            definition, on_press=self.on_click, on_press_outside=self.on_click_outside
        )
        super(FocusBox, self).__init__(definition)
        self.definition: FocusBoxDefinition = self.definition
        self._is_focused: bool = False

    def on_enter(self):
        """
        Called when this Box enters the Scene.

        Add it to the global focus stack.
        """
        super(FocusBox, self).on_enter()
        self.definition.focus_stack.register_focus_box(self)

    def on_exit(self):
        """
        Called when this Box exists the Scene.

        Remove it from the global focus stack.
        """
        super(FocusBox, self).on_exit()
        self.definition.focus_stack.unregister_focus_box(self)

    @property
    def is_focused(self) -> bool:
        """True if this Box is currently focused."""
        return self._is_focused

    @is_focused.setter
    def is_focused(self, value: bool) -> None:
        """Set whether this Box is focused or not."""
        if value:
            self.take_focus()
        else:
            self.lose_focus()

    def take_focus(self) -> bool:
        """
        Set this Box as focused.

        Move the parent to the top of the event stack.

        :return: True if focus was taken. False if this node was already focused.
        """
        if not self._is_focused:
            log.info(f"Taking focus: {self.parent}")
            self._is_focused = True
            self.definition.focus_stack.notify_focused(self)
            if self.definition.on_take_focus is not None:
                self.definition.on_take_focus()
            return True
        return False

    def lose_focus(self) -> bool:
        """
        Set this Box as not focused.

        :return: True if focus was lost. False if this node was not already focused.
        """
        if self._is_focused:
            self._is_focused = False
            if self.definition.on_lose_focus is not None:
                self.definition.on_lose_focus()
            log.info(f"Losing focus: {self.parent}")
            return True
        return False

    def on_click(
        self, box: "MouseBox", x: int, y: int, buttons: int, modifiers: int
    ) -> Optional[bool]:
        """Take focus when this Box is clicked."""
        self.take_focus()
        return EVENT_UNHANDLED

    def on_click_outside(
        self, box: "MouseBox", x: int, y: int, buttons: int, modifiers: int
    ) -> Optional[bool]:
        """Lose focus when a click occurs outside of this Box."""
        self.lose_focus()
        return EVENT_UNHANDLED


@dataclass(frozen=True)
class KeyboardFocusBoxDefinition(FocusBoxDefinition):
    """
    Definition of a FocusBox that focuses and associated KeyboardHandler when it is focused.

    This allows for a Box (and its children) to selectively receive keyboard events depending
    on whether they are focused or not.

    :param keyboard_handler: The KeyboardHandler to control the focus state of.
        If None, then a keyboard handler that is a sibling of this node will be used.
    """

    keyboard_handler: Optional[KeyboardHandler] = None


class KeyboardFocusBox(FocusBox):
    """A mouse box that when clicked causes its parent to take precedence on keyboard events."""

    def __init__(self, definition: KeyboardFocusBoxDefinition):
        """Create a new KeyboardFocusBox."""
        super(KeyboardFocusBox, self).__init__(definition)
        self.definition = cast(KeyboardFocusBoxDefinition, self.definition)

    @staticmethod
    def _set_focused_if_is_keyboard_handler(node: cocos.cocosnode.CocosNode) -> None:
        """Determine if the given node is a keyboard handler. If so, make it take focus."""
        if isinstance(node, KeyboardHandler):
            node.set_focused()

    @staticmethod
    def _set_unfocused_if_is_keyboard_handler(node: cocos.cocosnode.CocosNode) -> None:
        """Determine if the given node is a keyboard handler. If so, make it take focus."""
        if isinstance(node, KeyboardHandler):
            node.set_unfocused()

    def take_focus(self) -> bool:
        """Gain focus on all keyboard handlers that are children of the focus target."""
        took_focus = super(KeyboardFocusBox, self).take_focus()
        if took_focus:
            self.parent.walk(self._set_focused_if_is_keyboard_handler)
        return took_focus

    def lose_focus(self) -> bool:
        """Lost focus on all keyboard handlers that are children of the focus target."""
        lost_focus = super(KeyboardFocusBox, self).lose_focus()
        if lost_focus:
            self.parent.walk(self._set_unfocused_if_is_keyboard_handler)
        return lost_focus


class VisualAndKeyboardFocusBox(KeyboardFocusBox):
    """
    A Box that causes its target to become focused and move to the top of its parents children.

    This causes it to visually appear on top of all its siblings; and is therefore also able to
    receive mouse events first.
    """

    def take_focus(self) -> bool:
        """
        Set this Box as focused.

        Move the parent to the top of the event stack.

        :return: True if focus was taken. False if this node was already focused.
        """
        took_focus = super(VisualAndKeyboardFocusBox, self).take_focus()
        if took_focus:
            log.debug(f"Taking visual focus: {self}")
            # Set the parent z value to make this both appear on top and have event handlers
            # at the top of the stack.
            self.parent.set_z_value(ZIndexEnum.top)
        return took_focus

    def on_click(
        self, box: "MouseBox", x: int, y: int, buttons: int, modifiers: int
    ) -> Optional[bool]:
        """Take focus when this Box is clicked."""
        took_focus = self.take_focus()
        if took_focus:
            # Consume the event and re-submit it to take account of the updated event stack
            # caused by the focus change.
            log.debug(f"Resubmitted mouse_press_event for new focus stack: {self}")
            cocos.director.director.window.dispatch_event(
                "on_mouse_press", x, y, buttons, modifiers
            )
            return EVENT_HANDLED
        return EVENT_UNHANDLED


def make_focusable(
    box: Box,
    on_take_focus: Optional[Callable[[], None]] = None,
    on_lose_focus: Optional[Callable[[], None]] = None,
    focus_type: Type[FocusBox] = VisualAndKeyboardFocusBox,
) -> FocusBox:
    """
    Make the given Box focusable.

    This adds a FocusBox of the same size as the given Box to the Box.

    :param box: Box to make focusable.
    :param on_take_focus: Called with no arguments when the given box gains focus.
    :param on_lose_focus: Called with no arguments when the given box loses focus.
    :param focus_type: The type of focus box to use. Defaults to VisualAndKeyboardFocus.
    :return: Returns the FocusBox that was created.
    """
    defn = KeyboardFocusBoxDefinition(
        width=box.definition.width,
        height=box.definition.height,
        on_take_focus=on_take_focus,
        on_lose_focus=on_lose_focus,
    )
    focus_box = focus_type(defn)
    # Add the focus box as the last child so that its event handlers get pushed first.
    # Use z=10000 as this should be high enough to make sure that the FocusBox is always the first
    # child without having to keep moving it up the stack if another child with a higher z value
    # is added.
    box.add(focus_box, z=10000)
    return focus_box
