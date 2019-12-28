"""
Module defining nodes which can be focused.

A focused node:
  - consumes all mouse events within its area, preventing underlying nodes from receiving them.
  - gets first priority on keyboard event handling.

A common example of focus is handling overlapping windows - one appears on top of the other
and consumes all mouse events, preventing the one underneath from being accidentally interacted
with.
"""

import cocos

from typing import List, Optional

from ..data_structures import ZIndexEnum
from .box import Box, BoxDefinition
from .mouse_box import MouseBox, MouseBoxDefinition


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
            box.lose_focus()

    def notify_unfocused(self, focus_box: "FocusBox") -> None:
        """
        To be called when a focus box loses focus.

        Make the next highest FocusBox in the stack take focus, which will place that box
        higher in the stack.

        :param focus_box: The box that has been unfocused.
        """
        for box in self._focus_stack:
            if box is not focus_box:
                box.take_focus()
                break


# The global focus stack.
FocusStackHandler = _FocusStackHandler()


class FocusBox(MouseBox):
    """
    A Box that causes its target to become focused when clicked on.

    The focused target receives all events first.
    """

    def __init__(
        self, definition: BoxDefinition, focus_stack: _FocusStackHandler = None
    ):
        """
        Create a new FocusBox.

        Registers this FocusBox with the focus stack handler.

        :param definition: BoxDefinition defining the shape of the focus box.
        :param focus_stack: The focus stack to use. Defaults to the global singleton.
        """
        if focus_stack is None:
            focus_stack = FocusStackHandler
        self.focus_stack = focus_stack

        definition = MouseBoxDefinition(
            width=definition.width, height=definition.height, on_press=self.on_click
        )
        self._is_focused: bool = False
        self._original_z_value: int = 0
        super(FocusBox, self).__init__(definition)

    def on_enter(self):
        """
        Called when this Box enters the Scene.

        Add it to the global focus stack.
        """
        super(FocusBox, self).on_enter()
        self._original_z_value = self.get_z_value()
        self.focus_stack.register_focus_box(self)

    def on_exit(self):
        """
        Called when this Box exists the Scene.

        Remove it from the global focus stack.
        """
        super(FocusBox, self).on_exit()
        self.focus_stack.unregister_focus_box(self)

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

        Add the parents, and all its childrens, event handlers to the top of the event stack.

        This means that their event handlers will be in the stack twice.

        These additional handlers will be removed when focus is lost.

        :return: True if focus was taken. False if this node was already focused.
        """
        if not self._is_focused:
            self._is_focused = True
            self.focus_stack.notify_focused(self)
            # Set the parent z value to make this both appear on top and have event handlers
            # at the top of the stack.
            self.parent.set_z_value(ZIndexEnum.top)
            return True
        return False

    def lose_focus(self) -> bool:
        """
        Set this Box as not focused.

        Remove the parents, and all its childrens, event handlers from the event stack.
        This removes the extra handlers added when focus was gained, and leaves the original
        handlers in place.

        :return: True if focus was lost. False if this node was not already focused.
        """
        if self._is_focused:
            self._is_focused = False
            self.parent.set_z_value(self._original_z_value)
            self.focus_stack.notify_unfocused(self)
            return True
        return False

    def on_click(
        self, box: "MouseBox", x: int, y: int, buttons: int, modifiers: int
    ) -> bool:
        """
        Take focus when this Box is clicked.

        Consumes the click event, and re-dispatch it as the change in focus will change the
        event stack.
        """
        took_focus: bool = self.take_focus()
        if took_focus:
            # Consume the event and re-submit it to take account of the new event stack.
            cocos.director.director.window.dispatch_event(
                "on_mouse_press", x, y, buttons, modifiers
            )
            return True
        # Otherwise don't consume the event.
        return False


def make_focusable(box: Box) -> FocusBox:
    """
    Make the given Box focusable.

    This adds a FocusBox of the same size as the given Box to the Box.

    :param box: Box to make focusable.
    :return: Returns the FocusBox that was created.
    """
    focus_box = FocusBox(box.definition)
    # Add the focus box as the last child so that its event handlers get pushed first.
    # Use z=10000 as this should be high enough to make sure that the FocusBox is always the first
    # child without having to keep moving it up the stack if another child with a higher z value
    # is added.
    box.add(focus_box, z=10000)
    return focus_box
