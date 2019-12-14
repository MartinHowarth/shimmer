"""Definition of a Button."""

import cocos
import logging


from dataclasses import dataclass, field
from typing import Optional, Callable, Tuple, Dict, Union
from pyglet.event import EVENT_UNHANDLED, EVENT_HANDLED

from shimmer.display.data_structures import Color
from shimmer.display.primitives import create_rect
from shimmer.display.components.box import ActiveBox


log = logging.getLogger(__name__)

Point2d = Tuple[int, int]


@dataclass
class Callback:
    """Definition of a function callback with arguments."""

    method: Callable
    args: Tuple = field(default_factory=tuple)
    kwargs: Dict = field(default_factory=dict)

    def activate(self, **kwargs):
        """Call the defined callback, passing in any extra arguments from `kwargs`."""
        kwargs.update(self.kwargs)
        self.method(*self.args, **kwargs)


@dataclass
class ButtonDefinition:
    """
    Definition of an invisible button that can be clicked and hovered over.

    Method definitions can be one of:
      - Callable - called with no arguments
      - Callback - called with defined arguments as well as the mouse event arguments
    """

    on_press: Optional[Union[Callback, Callable]] = None
    on_release: Optional[Union[Callback, Callable]] = None
    on_hover: Optional[Union[Callback, Callable]] = None
    on_unhover: Optional[Union[Callback, Callable]] = None
    on_drag: Optional[Union[Callback, Callable]] = None


@dataclass
class VisibleButtonDefinition(ButtonDefinition):
    """A Button definition with visual elements."""

    text: Optional[str] = None
    base_color: Color = Color(0, 111, 255)
    depressed_color: Optional[Color] = None
    hover_color: Optional[Color] = None


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


class Button(ActiveBox):
    """A box that reacts to mouse events."""

    def __init__(
        self, definition: ButtonDefinition, rect: Optional[cocos.rect.Rect] = None,
    ):
        """
        Creates a new Button.

        :param definition: Definition of the Button to attach to the box.
        :param rect: Rectangular area that triggers the button.
        """
        super(Button, self).__init__(rect)
        self.definition: ButtonDefinition = definition
        self._currently_hovered: bool = False

        # bitwise representation of pressed buttons, as pyglet defines them.
        self._currently_pressed: int = 0

    def _on_press(self, x, y, buttons, modifiers):
        """
        Called when the button is clicked by the user.

        Calls the `on_press` callback from the definition, passing information about the click to
        to callback.
        """
        log.debug(f"Button {self!r} pressed.")
        self._currently_pressed = bitwise_add(self._currently_pressed, buttons)

        if self.definition.on_press is None:
            return

        if isinstance(self.definition.on_press, Callback):
            self.definition.on_press.activate(
                x=x, y=y, buttons=buttons, modifiers=modifiers
            )
        else:
            self.definition.on_press()

    def _on_release(self, x, y, buttons, modifiers):
        """
        Called when the mouse is released by the user within the button area.

        Not guaranteed to be called on every button press as the user may move the mouse off
        the button before releasing.

        Calls the `on_release` callback from the definition, passing information about the click to
        to callback.
        """
        log.debug(f"Button {self!r} released.")
        self._currently_pressed = bitwise_remove(self._currently_pressed, buttons)

        if self.definition.on_release is None:
            return

        if isinstance(self.definition.on_release, Callback):
            self.definition.on_release.activate(
                x=x, y=y, buttons=buttons, modifiers=modifiers
            )
        else:
            self.definition.on_release()

    def _on_hover(self, x, y, dx, dy):
        """
        Called when the user moves the mouse over the button without any mouse buttons pressed.

        Calls the `on_hover` callback from the definition, passing information about the click to
        to callback.
        """
        if self.definition.on_hover is None:
            return

        if isinstance(self.definition.on_hover, Callback):
            self.definition.on_hover.activate(x=x, y=y, dx=dx, dy=dy)
        else:
            self.definition.on_hover()

    def _on_unhover(self, x, y, dx, dy):
        """
        Called when the user moves the mouse off the button without any mouse buttons pressed.

        Calls the `on_unhover` callback from the definition, passing information about the click to
        to callback.
        """
        # reset knowledge of which mouse buttons are pressed when mouse leaves the button.
        self._currently_pressed = 0

        if self.definition.on_unhover is None:
            return

        if isinstance(self.definition.on_unhover, Callback):
            self.definition.on_unhover.activate(x=x, y=y, dx=dx, dy=dy)
        else:
            self.definition.on_unhover()

    def _should_handle_mouse_press(self, buttons: int) -> bool:
        """
        Determine if this button should attempt to handle the mouse press event.

        :param buttons: Int indicating which buttons are pressed (see pyglet).
        :return: True if this button should handle the mouse click press.
        """
        return self.definition.on_press is not None

    def _should_handle_mouse_release(self, buttons: int) -> bool:
        """
        Determine if this button should attempt to handle the mouse release event.

        This checks if this button was previously pressed with the same mouse button.
        This prevents the user clicking off the button, moving onto it and then releasing.

        :param buttons: Int indicating which buttons are pressed (see pyglet).
        :return: True if this button should handle the mouse click release.
        """
        return self.definition.on_release is not None and bitwise_contains(
            self._currently_pressed, buttons
        )

    def _should_handle_mouse_hover(self) -> bool:
        """
        Determine if this button should attempt to handle the mouse hover event.

        :return: True if this button should handle the mouse hover event.
        """
        return self.definition.on_hover is not None

    def on_mouse_press(self, x, y, buttons, modifiers):
        """
        Cocos director callback when the mouse is pressed.

        Checks if the event happened in the area defined by this button and, if so, handles it.
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

        Checks if the event happened in the area defined by this button and, if so, handles it.
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

        Checks if the mouse moved onto or off the button and triggers a hover or unhover event
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


class VisibleButton(Button):
    """
    A Button that has visual elements.

    Changes color when hovered over or clicked on.
    """

    definition: VisibleButtonDefinition

    def __init__(
        self,
        definition: VisibleButtonDefinition,
        rect: Optional[cocos.rect.Rect] = None,
    ):
        """Creates a new VisibleButton."""
        super(VisibleButton, self).__init__(definition, rect)
        self.label: Optional[cocos.text.Label] = None
        self.color_rect: cocos.layer.ColorLayer = None
        self.update_label()
        self.update_color_layer()

    @property
    def rect(self) -> cocos.rect.Rect:
        return self._rect

    @rect.setter
    def rect(self, value: cocos.rect.Rect):
        self._rect = value
        self.update_label()
        self.update_color_layer()

    def update_label(self):
        """Recreate the button label."""
        if self.definition.text is None:
            self.label = None
            return

        if self.label is not None:
            self.remove(self.label)

        self.label = cocos.text.Label(
            self.definition.text,
            font_name="calibri",
            font_size=16,
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )
        self.label.position = self.rect.width / 2, self.rect.height / 2
        self.add(self.label)

    def update_color_layer(self):
        """Recreate the button color layer."""
        if self.color_rect is not None:
            self.remove(self.color_rect)

        # Include the `or 1` to override cocos default behaviour to make the
        # layer the size of the entire window.
        self.color_rect = create_rect(
            self.rect.width or 1, self.rect.height or 1, self.definition.base_color
        )
        self.add(self.color_rect, z=-1)

    def _should_handle_mouse_press(self, buttons) -> bool:
        """Whether this button should handle mouse press events."""
        return (
            self.definition.on_press is not None
            # Also handle if on_release is defined so we can record which mouse button was used.
            or self.definition.on_release is not None
            or self.definition.depressed_color is not None
        )

    def _should_handle_mouse_release(self, buttons) -> bool:
        """Whether this button should handle mouse release events."""
        return (
            # Also handle if on_press is defined so we can record which mouse button was used.
            self.definition.on_press is not None
            or self.definition.on_release is not None
            or self.definition.depressed_color is not None
        ) and bitwise_contains(self._currently_pressed, buttons)

    def _should_handle_mouse_hover(self) -> bool:
        """Whether this button should handle mouse hover and unhover events."""
        return (
            self.definition.on_hover is not None
            or self.definition.on_unhover is not None
            or self.definition.hover_color is not None
        )

    def _on_press(self, x, y, buttons, modifiers):
        """Change the button color and call the on_press callback."""
        super(VisibleButton, self)._on_press(x, y, buttons, modifiers)
        if self.definition.depressed_color is not None:
            self.color_rect.color = self.definition.depressed_color.as_tuple()
            # self.color_rect.opacity = self.definition.depressed_color.a

    def _on_release(self, x, y, buttons, modifiers):
        """Change the button color and call the on_release callback."""
        super(VisibleButton, self)._on_release(x, y, buttons, modifiers)
        if self._currently_hovered:
            if self.definition.hover_color is not None:
                self.color_rect.color = self.definition.hover_color.as_tuple()
                # self.color_rect.opacity = self.definition.hover_color.a
        else:
            self.color_rect.color = self.definition.base_color.as_tuple()
            # self.color_rect.opacity = self.definition.base_color.a

    def _on_hover(self, x, y, dx, dy):
        """Change the button color and call the on_hover callback."""
        super(VisibleButton, self)._on_hover(x, y, dx, dy)
        if self.definition.hover_color is not None:
            self.color_rect.color = self.definition.hover_color.as_tuple()
            # self.color_rect.opacity = self.definition.hover_color.a

    def _on_unhover(self, x, y, dx, dy):
        """Change the button color and call the on_unhover callback."""
        super(VisibleButton, self)._on_unhover(x, y, dx, dy)
        if self.definition.hover_color is not None:
            self.color_rect.color = self.definition.base_color.as_tuple()
            # self.color_rect.opacity = self.definition.base_color.a
