"""Definition of a Box that responds in a user-defined way to mouse events."""

import cocos
import logging


from dataclasses import dataclass, replace
from typing import Optional, Protocol
from pyglet.event import EVENT_UNHANDLED, EVENT_HANDLED

from shimmer.display.primitives import Point2d
from shimmer.display.components.box import ActiveBox, Box


log = logging.getLogger(__name__)


class MouseEventCallable(Protocol):
    """Protocol defining the type for any callback performed by a MouseBox."""

    def __call__(
        self,
        parent: "MouseBox",  # This is the MouseBox that handled the event.
        x: int,
        y: int,
        dx: Optional[int] = None,
        dy: Optional[int] = None,
        buttons: Optional[int] = None,
        modifiers: Optional[int] = None,
    ) -> None:
        """
        The signature of mouse event callbacks.

        The following parameters depend on the event that has occurred - see pyglet documentation:
            (dx, dy) are always given together; but not always given.
            (buttons, modifiers) are always given together; but not always given.
        """
        pass


@dataclass
class MouseBoxDefinition:
    """
    Definition of an invisible Box that can be clicked and hovered over.

    Method definitions are optional and are called with the mouse event arguments as keywords.
    """

    parent: Optional[Box] = None
    on_press: Optional[MouseEventCallable] = None
    on_release: Optional[MouseEventCallable] = None
    on_hover: Optional[MouseEventCallable] = None
    on_unhover: Optional[MouseEventCallable] = None
    on_drag: Optional[MouseEventCallable] = None


def bundle_callables(*callables: MouseEventCallable) -> MouseEventCallable:
    """
    Bundle many callables into a single function.

    This allows for an event callable defined in MouseBoxDefinition to take multiple actions.

    Callables will be invoked in the order given.
    """

    def bundle_callables_inner(
        parent: MouseBox,
        x: int,
        y: int,
        dx: Optional[int] = None,
        dy: Optional[int] = None,
        buttons: Optional[int] = None,
        modifiers: Optional[int] = None,
    ):
        """Signature varies depending on which mouse event is called."""
        for method in callables:
            method(
                parent=parent,
                x=x,
                y=y,
                dx=dx,
                dy=dy,
                buttons=buttons,
                modifiers=modifiers,
            )

    return bundle_callables_inner


def bitwise_add(a: int, b: int) -> int:
    """Merge two binary masks together."""
    return a | b


def bitwise_remove(a: int, b: int) -> int:
    """Remove a binary mask from another mask."""
    if bitwise_contains(a, b):
        return a ^ b
    return a


def bitwise_contains(a: int, b: int) -> bool:
    """Return True if the mask `b` is contained in `a`."""
    return bool(a & b)


class MouseBox(ActiveBox):
    """A box that reacts to mouse events."""

    def __init__(
        self, definition: MouseBoxDefinition, rect: Optional[cocos.rect.Rect] = None,
    ):
        """
        Creates a new MouseBox.

        :param definition: Definition of the actions to take.
        :param rect: Rectangular area that the Box will consider mouses events from.
        """
        super(MouseBox, self).__init__(rect)
        self.definition: MouseBoxDefinition = replace(definition, parent=self)

        # Whether the mouse is currently hovered over the Box or not.
        self._currently_hovered: bool = False

        # Used to record whether we're currently dragging this Box.
        # This is needed because if the user drags too fast then we can't just rely on
        # a drag event being inside the box area still.
        self._currently_dragging: bool = False

        # bitwise representation of pressed buttons, as pyglet defines them.
        self._currently_pressed: int = 0

    def _on_press(self, x, y, buttons, modifiers):
        """
        Called when the Box is clicked by the user.

        Calls the `on_press` callback from the definition, passing information about the click to
        to callback.
        """
        log.debug(f"Button {self!r} pressed.")
        self._currently_pressed = bitwise_add(self._currently_pressed, buttons)

        if self.definition.on_press is None:
            return

        self.definition.on_press(
            parent=self, x=x, y=y, buttons=buttons, modifiers=modifiers
        )

    def _on_release(self, x, y, buttons, modifiers):
        """
        Called when the mouse is released by the user within the button area.

        Not guaranteed to be called after every mouse click as the user may move the mouse off
        the Box before releasing.

        Calls the `on_release` callback from the definition, passing information about the click to
        to callback.
        """
        log.debug(f"Button {self!r} released.")
        self._currently_pressed = bitwise_remove(self._currently_pressed, buttons)

        if self.definition.on_release is None:
            return

        self.definition.on_release(
            parent=self, x=x, y=y, buttons=buttons, modifiers=modifiers
        )

    def _on_hover(self, x, y, dx, dy):
        """
        Called when the user moves the mouse over the Box without any mouse buttons pressed.

        Calls the `on_hover` callback from the definition, passing information about the click to
        to callback.
        """
        if self.definition.on_hover is None:
            return

        self.definition.on_hover(parent=self, x=x, y=y, dx=dx, dy=dy)

    def _on_unhover(self, x, y, dx, dy):
        """
        Called when the user moves the mouse off the Box without any mouse buttons pressed.

        Calls the `on_unhover` callback from the definition, passing information about the click to
        to callback.
        """
        # reset knowledge of which mouse buttons are pressed when mouse leaves the button.
        self._currently_pressed = 0

        if self.definition.on_unhover is None:
            return

        self.definition.on_unhover(parent=self, x=x, y=y, dx=dx, dy=dy)

    def _on_drag(self, x, y, dx, dy, buttons, modifiers):
        """
        Called when the mouse is moved by the user with a mouse button pressed.

        Calls the `on_drag` callback from the definition, passing information about the event to
        to callback.
        """
        if self.definition.on_drag is None:
            return

        self.definition.on_drag(
            parent=self, x=x, y=y, dx=dx, dy=dy, buttons=buttons, modifiers=modifiers
        )

    def _should_handle_mouse_press(self, buttons: int) -> bool:
        """
        Determine if this Box should attempt to handle the mouse press event.

        :param buttons: Int indicating which mouse buttons are pressed (see pyglet).
        :return: True if this Box should handle the mouse click press.
        """
        return self.definition.on_press is not None

    def _should_handle_mouse_release(self, buttons: int) -> bool:
        """
        Determine if this Box should attempt to handle the mouse release event.

        This checks if this Box was previously pressed with the same mouse button.
        This prevents the user clicking off the Box, moving onto it and then releasing.

        :param buttons: Int indicating which mouse buttons are pressed (see pyglet).
        :return: True if this Box should handle the mouse click release.
        """
        return self.definition.on_release is not None and bitwise_contains(
            self._currently_pressed, buttons
        )

    def _should_handle_mouse_hover(self) -> bool:
        """
        Determine if this Box should attempt to handle the mouse hover event.

        :return: True if this Box should handle the mouse hover event.
        """
        return self.definition.on_hover is not None

    def _should_handle_mouse_drag(self) -> bool:
        """
        Determine if this Box should attempt to handle a mouse drag event.

        :return: True if this Box should handle the mouse drag event.
        """
        return self._currently_dragging and self.definition.on_drag is not None

    def on_mouse_press(self, x, y, buttons, modifiers):
        """
        Cocos director callback when the mouse is pressed.

        Checks if the event happened in the area defined by this Box and, if so, handles it.
        """
        if not self._should_handle_mouse_press(buttons):
            return EVENT_UNHANDLED

        coord: Point2d = cocos.director.director.get_virtual_coordinates(x, y)
        if self.contains_coord(*coord):
            self._on_press(*coord, buttons, modifiers)
            return EVENT_HANDLED

    def on_mouse_release(self, x, y, buttons, modifiers):
        """
        Cocos director callback when the mouse is release.

        Checks if the event happened in the area defined by this Box and, if so, handles it.
        """
        if not self._should_handle_mouse_release(buttons):
            return EVENT_UNHANDLED

        coord: Point2d = cocos.director.director.get_virtual_coordinates(x, y)
        if self.contains_coord(*coord):
            self._on_release(*coord, buttons, modifiers)
            return EVENT_HANDLED

    def on_mouse_motion(self, x, y, dx, dy):
        """
        Cocos director callback when the mouse is moved.

        Checks if the mouse moved onto or off the Box and triggers a hover or unhover event
        respectively.

        Does not capture the event, so it may be handled by other entities as well.
        """
        if not self._should_handle_mouse_hover():
            return EVENT_UNHANDLED

        coord: Point2d = cocos.director.director.get_virtual_coordinates(x, y)
        if self.contains_coord(*coord):
            if not self._currently_hovered:
                self._currently_hovered = True
                self._on_hover(*coord, dx, dy)
            # Do not return EVENT_HANDLED on hover as we could be hovering over multiple things.
        elif self._currently_hovered:
            self._currently_hovered = False
            self._on_unhover(*coord, dx, dy)
            # Do not return EVENT_HANDLED on unhover as we have left the button area.

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Cocos director callback when the mouse is moved while a mouse button is pressed."""
        if not self._should_handle_mouse_drag():
            return EVENT_UNHANDLED

        # We don't check for this event being within the bounds of the Box because we instead rely
        # on the setting of `self._currently_dragging` via another method (e.g. click/release) to
        # control whether drag events should be handled or not.
        coord: Point2d = cocos.director.director.get_virtual_coordinates(x, y)
        self._on_drag(*coord, dx, dy, buttons, modifiers)
        return EVENT_HANDLED
