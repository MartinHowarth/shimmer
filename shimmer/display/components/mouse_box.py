"""Definition of a Box that responds in a user-defined way to mouse events."""

import cocos
import logging

from dataclasses import dataclass
from typing import Optional, Protocol
from pyglet.event import EVENT_UNHANDLED, EVENT_HANDLED

from shimmer.display.helpers import bitwise_add, bitwise_remove, bitwise_contains
from shimmer.display.primitives import Point2d
from shimmer.display.components.box import ActiveBox, BoxDefinition

log = logging.getLogger(__name__)


class MouseClickEventCallable(Protocol):
    """Protocol defining the signature of on_press and on_release callbacks."""

    def __call__(
        self,
        box: "MouseBox",  # This is the MouseBox that handled the event.
        x: int,
        y: int,
        buttons: int,
        modifiers: int,
    ) -> Optional[bool]:
        """
        The signature of mouse click event callbacks.

        Return True or None to consume the mouse event.
        Return False to allow it to propagate to other handlers.
        """


class MouseMotionEventCallable(Protocol):
    """Protocol defining the signature of on_hover and on_unhover callbacks."""

    def __call__(
        self,
        box: "MouseBox",  # This is the MouseBox that handled the event.
        x: int,
        y: int,
        dx: int,
        dy: int,
    ) -> Optional[bool]:
        """
        The signature of mouse motion event callbacks.

        Important note: The default (i.e. return None) is that mouse motion callbacks do not
            consume the event, which is different to Click or Drag events.

        Return True to consume the mouse event.
        Return False or None to allow it to propagate to other handlers.
        """


class MouseDragEventCallable(Protocol):
    """Protocol defining the signature of on_drag callback."""

    def __call__(
        self,
        box: "MouseBox",  # This is the MouseBox that handled the event.
        x: int,
        y: int,
        dx: int,
        dy: int,
        buttons: int,
        modifiers: int,
    ) -> Optional[bool]:
        """
        The signature of mouse drag event callbacks.

        Return True or None to consume the mouse event.
        Return False to allow it to propagate to other handlers.
        """


@dataclass(frozen=True)
class MouseBoxDefinition(BoxDefinition):
    """
    Definition of an invisible Box that can be clicked and hovered over.

    Method definitions are optional and are called with the mouse event arguments as keywords.

    :param on_press: Called when a mouse button is pressed within the Box.
    :param on_release: Called when a mouse button is released within the Box.
        Note: This may not always follow an `on_press` because the user may drag outside the box
        before releasing the mouse button.
    :param on_hover: Called when the mouse enters the Box.
    :param on_unhover: Called when the mouse leaves the Box.
    :param on_motion: Called when the mouse moves within the Box.
    :param on_drag: Called when the mouse moves within the Box while mouse buttons are pressed.
    """

    on_press: Optional[MouseClickEventCallable] = None
    on_release: Optional[MouseClickEventCallable] = None
    on_hover: Optional[MouseMotionEventCallable] = None
    on_unhover: Optional[MouseMotionEventCallable] = None
    on_motion: Optional[MouseMotionEventCallable] = None
    on_drag: Optional[MouseDragEventCallable] = None


@dataclass(frozen=True)
class MouseVoidBoxDefinition(MouseBoxDefinition):
    """Definition of a mouse box that swallows all mouse events."""

    @staticmethod
    def do_nothing(*_, **__):
        """Do nothing on the event, and return True to mark the event as handled."""
        return True

    on_press: Optional[MouseClickEventCallable] = do_nothing
    on_release: Optional[MouseClickEventCallable] = do_nothing
    on_hover: Optional[MouseMotionEventCallable] = do_nothing
    on_unhover: Optional[MouseMotionEventCallable] = do_nothing
    on_motion: Optional[MouseMotionEventCallable] = do_nothing
    on_drag: Optional[MouseDragEventCallable] = do_nothing


class MouseBox(ActiveBox):
    """A box that reacts to mouse events."""

    definition_type = MouseBoxDefinition

    def __init__(self, definition: MouseBoxDefinition):
        """
        Creates a new MouseBox.

        :param definition: Definition of the actions to take.
        """
        super(MouseBox, self).__init__(definition)
        self.definition: MouseBoxDefinition = definition

        # Whether the mouse is currently hovered over the Box or not.
        self._currently_hovered: bool = False

        # Used to record whether we're currently dragging this Box.
        # This is needed because if the user drags too fast then we can't just rely on
        # a drag event being inside the box area still.
        self._currently_dragging: bool = False

        # bitwise representation of pressed buttons, as pyglet defines them.
        self._currently_pressed: int = 0

    def _on_press(self, x: int, y: int, buttons: int, modifiers: int) -> Optional[bool]:
        """
        Called when the Box is clicked by the user.

        Calls the `on_press` callback from the definition, passing information about the event to
        the callback.
        """
        log.debug(f"Button {buttons} pressed on {self}.")
        if buttons is not None:
            self._currently_pressed = bitwise_add(self._currently_pressed, buttons)

        if self.definition.on_press is None:
            return None

        return self.definition.on_press(
            box=self, x=x, y=y, buttons=buttons, modifiers=modifiers
        )

    def _on_release(
        self, x: int, y: int, buttons: int, modifiers: int
    ) -> Optional[bool]:
        """
        Called when the mouse is released by the user within the button area.

        Not guaranteed to be called after every mouse click as the user may move the mouse off
        the Box before releasing.

        Calls the `on_release` callback from the definition, passing information about the event to
        the callback.
        """
        log.debug(f"Button {buttons} released on {self}.")

        if self.definition.on_release is not None:
            result = self.definition.on_release(
                box=self, x=x, y=y, buttons=buttons, modifiers=modifiers
            )
        else:
            result = None

        # Remove from currently selected after the on_release callback in case it is needed
        # in a sub class.
        if buttons is not None:
            self._currently_pressed = bitwise_remove(self._currently_pressed, buttons)

        return result

    def _on_hover(self, x: int, y: int, dx: int, dy: int) -> Optional[bool]:
        """
        Called when the user moves the mouse over the Box without any mouse buttons pressed.

        Calls the `on_hover` callback from the definition, passing information about the event to
        the callback.
        """
        self._currently_hovered = True

        if self.definition.on_hover is None:
            return None

        return self.definition.on_hover(box=self, x=x, y=y, dx=dx, dy=dy)

    def _on_motion(self, x: int, y: int, dx: int, dy: int) -> Optional[bool]:
        """
        Called when the user moves the mouse within the Box without any mouse buttons pressed.

        Calls the `on_motion` callback from the definition, passing information about the event to
        the callback.
        """
        if self.definition.on_motion is None:
            return None

        return self.definition.on_motion(box=self, x=x, y=y, dx=dx, dy=dy)

    def _on_unhover(self, x: int, y: int, dx: int, dy: int) -> Optional[bool]:
        """
        Called when the user moves the mouse off the Box without any mouse buttons pressed.

        Calls the `on_unhover` callback from the definition, passing information about the event to
        the callback.
        """
        # reset knowledge of which mouse buttons are pressed when mouse leaves the button.
        self._currently_pressed = 0
        self._currently_hovered = False

        if self.definition.on_unhover is None:
            return None

        return self.definition.on_unhover(box=self, x=x, y=y, dx=dx, dy=dy)

    def _on_drag(
        self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
    ) -> Optional[bool]:
        """
        Called when the mouse is moved by the user with a mouse button pressed.

        Calls the `on_drag` callback from the definition, passing information about the event to
        the callback.
        """
        if self.definition.on_drag is None:
            return None

        return self.definition.on_drag(
            box=self, x=x, y=y, dx=dx, dy=dy, buttons=buttons, modifiers=modifiers
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
        Determine if this Box should attempt to handle mouse hover and unhover events.

        :return: True if this Box should handle mouse hover and unhover events.
        """
        return (
            self.definition.on_hover is not None
            or self.definition.on_unhover is not None
        )

    def _should_handle_mouse_motion(self) -> bool:
        """
        Determine if this Box should attempt to handle mouse motion events.

        :return: True if this Box should handle mouse motion events.
        """
        return self.definition.on_motion is not None

    def _should_handle_mouse_drag(self) -> bool:
        """
        Determine if this Box should attempt to handle a mouse drag event.

        :return: True if this Box should handle the mouse drag event.
        """
        return self._currently_dragging and self.definition.on_drag is not None

    def on_mouse_press(
        self, x: int, y: int, buttons: int, modifiers: int
    ) -> Optional[bool]:
        """
        Cocos director callback when the mouse is pressed.

        Checks if the event happened in the area defined by this Box and, if so, handles it.
        """
        if not self._should_handle_mouse_press(buttons):
            return EVENT_UNHANDLED

        coord: Point2d = cocos.director.director.get_virtual_coordinates(x, y)
        if self.contains_coord(*coord):
            result = self._on_press(*coord, buttons, modifiers)
            return EVENT_HANDLED if result in [True, None] else EVENT_UNHANDLED
        return EVENT_UNHANDLED

    def on_mouse_release(
        self, x: int, y: int, buttons: int, modifiers: int
    ) -> Optional[bool]:
        """
        Cocos director callback when the mouse is release.

        Checks if the event happened in the area defined by this Box and, if so, handles it.
        """
        if not self._should_handle_mouse_release(buttons):
            return EVENT_UNHANDLED

        coord: Point2d = cocos.director.director.get_virtual_coordinates(x, y)
        if self.contains_coord(*coord):
            result = self._on_release(*coord, buttons, modifiers)
            return EVENT_HANDLED if result in [True, None] else EVENT_UNHANDLED
        return EVENT_UNHANDLED

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> Optional[bool]:
        """
        Cocos director callback when the mouse is moved.

        Checks if the mouse moved onto or off the Box and triggers a hover or unhover event
        respectively.

        By default does not capture the event, so it may be handled by other entities as well.
        """
        if (
            not self._should_handle_mouse_hover()
            and not self._should_handle_mouse_motion()
        ):
            return EVENT_UNHANDLED

        result: Optional[bool] = None
        coord: Point2d = cocos.director.director.get_virtual_coordinates(x, y)
        if self.contains_coord(*coord):
            if not self._currently_hovered:
                result = self._on_hover(*coord, dx, dy)

            # If on_hover hasn't already handled the event, call on_motion.
            if result is not True:
                result = self._on_motion(*coord, dx, dy)

            # By default, do not return EVENT_HANDLED on hover as we could be
            # hovering over multiple things.
        elif self._currently_hovered:
            result = self._on_unhover(*coord, dx, dy)
            # By default, do not return EVENT_HANDLED on unhover as we have left
            # the button area.

        return EVENT_HANDLED if result in [True] else EVENT_UNHANDLED

    def on_mouse_drag(
        self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
    ) -> Optional[bool]:
        """Cocos director callback when the mouse is moved while a mouse button is pressed."""
        if not self._should_handle_mouse_drag():
            return EVENT_UNHANDLED

        # We don't check for this event being within the bounds of the Box because we instead rely
        # on the setting of `self._currently_dragging` via another method (e.g. click/release) to
        # control whether drag events should be handled or not.
        coord: Point2d = cocos.director.director.get_virtual_coordinates(x, y)
        result = self._on_drag(*coord, dx, dy, buttons, modifiers)
        return EVENT_HANDLED if result in [True, None] else EVENT_UNHANDLED

    def start_dragging(self, *_, **__):
        """Callback to start dragging this Box."""
        self._currently_dragging = True

    def stop_dragging(self, *_, **__):
        """Callback to stop dragging this Box."""
        self._currently_dragging = False
