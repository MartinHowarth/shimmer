"""Module defining ways for users to draw shapes."""

import cocos
import pyglet

from abc import ABC
from cocos.euclid import Point2, Vector2

from dataclasses import dataclass, replace
from typing import Dict, Callable, Optional, Tuple

from ..data_structures import ActiveGreen, Color
from ..components.box import BoxDefinition
from .mouse_box import MouseBox, MouseBoxDefinition


# Deliberately not frozen so we can update it as the rect is drawn.
@dataclass
class MouseDefinedRect:
    """
    Definition of a rect drawn by the mouse.

    Stores the coordinates of the dragged out rect, and which mouse buttons or keyboard
    modifiers were used at the start of the drawing.

    The minimum size is a 1x1 box. This is useful when the user performs a click
    without moving the mouse - you still get a non-zero rect which can intersect with other
    rects and/or be drawn as a single pixel.
    """

    # The drawing box that this rect was drawn in.
    canvas: "RectDrawingBox"
    buttons: int
    modifiers: int
    start_coord: Point2
    end_coord: Point2

    @property
    def vector(self) -> Vector2:
        """Vector from the start to the end coordinate."""
        return self.end_coord - self.start_coord

    @property
    def bottom_left(self) -> Point2:
        """
        The bottom-left point of the define rectangle.

        Accounts for rects drawn in any direction, i.e. it doesn't matter if the
        start coordinate is higher than the end coordinate.
        """
        return Point2(
            int(min(self.start_coord.x, self.end_coord.x)),
            int(min(self.start_coord.y, self.end_coord.y)),
        )

    @property
    def modifiers_as_string(self) -> str:
        """Return a string representing the modifiers used during drawing of this rect."""
        return pyglet.window.key.modifiers_string(self.modifiers)

    @property
    def dimensions(self) -> Tuple[int, int]:
        """Return the (width, height) of the defined rect, with a miniumum of (1, 1)."""
        move_vector = self.vector
        # Include the "or 1" to set the minimum size to be a 1x1 rect.
        # This both makes this a useful default to be a non-zero sized rect, but
        # also works around the cocos default of setting a rect to the full window size
        # if a dimension is 0.
        width, height = int(abs(move_vector[0])) or 1, int(abs(move_vector[1])) or 1
        return width, height

    def as_rect(self) -> cocos.rect.Rect:
        """Return the defined rect in coordinates relative to the canvas it was drawn on."""
        return cocos.rect.Rect(*self.bottom_left, *self.dimensions)

    def as_world_rect(self) -> cocos.rect.Rect:
        """Return the defined rect in world coordinates."""
        x, y = self.canvas.point_to_world(self.bottom_left)
        return cocos.rect.Rect(x, y, *self.dimensions)


@dataclass(frozen=True)
class RectDrawingBoxDefinition:
    """
    Definition of a box that the user can draw rectangles inside.

    Callbacks are given for start, change and completion of the drawing.

    The rect will be displayed during drawing using the defined color.
    """

    on_start: Optional[Callable[[MouseDefinedRect], None]] = None
    on_change: Optional[Callable[[MouseDefinedRect], None]] = None
    on_complete: Optional[Callable[[MouseDefinedRect], None]] = None
    color: Color = replace(ActiveGreen, a=100)


class DrawingBox(ABC, MouseBox):
    """Base class for defining boxes that can be drawn inside."""

    def __init__(self, definition: BoxDefinition):
        """
        Creates a new DrawableBox.

        :param definition: Definition of the shape of this Box.
        """
        definition = MouseBoxDefinition(
            width=definition.width,
            height=definition.height,
            on_press=self.on_press,
            on_release=self.on_release,
            on_drag=self.on_drag,
        )
        super(DrawingBox, self).__init__(definition)

    def on_press(
        self, box: MouseBox, x: int, y: int, buttons: int, modifiers: int,
    ) -> None:
        """Placeholder for subclasses to define what happens when a drawing begins."""
        pass

    def on_release(
        self, box: MouseBox, x: int, y: int, buttons: int, modifiers: int
    ) -> None:
        """Placeholder for subclasses to define what happens when a drawing is completed."""
        pass

    def on_drag(
        self,
        box: MouseBox,
        x: int,
        y: int,
        dx: int,
        dy: int,
        buttons: int,
        modifiers: int,
    ) -> None:
        """Placeholder for subclasses to define what happens when a drawing changes."""
        pass


class RectDrawingBox(DrawingBox):
    """
    A RectDrawingBox defines a rectangular area where Rects can be drawn using the mouse.

    The `on_complete` method in the definition is called every time a mouse button is
    released, returning the rect that was defined with that current set of buttons pressed.
    Multiple rects are recorded at once for each combination of mouse buttons that is pressed.

    Worked example:
        - Press left mouse button, start defining rect A at (L1, L2)
        - Move to (R1, R2)
        - Press right mouse button, start defining rect B at (R1, R2)
        - Move to (R3, R4)
        - Release right mouse button, call on_complete with rect defined by (R1, R2, R3, R4) with
            a MouseDefinedRect indicating that both left and right buttons are pressed.
        - Release left mouse button, call on_complete with rect defined by (L1, L2, R3, R4) with
            a MouseDefinedRect indicating that only the left button is pressed.
    """

    def __init__(
        self,
        definition: RectDrawingBoxDefinition,
        rect: Optional[cocos.rect.Rect] = None,
    ):
        """
        Creates a new RectDrawingBox.

        :param rect: Definition of the rectangle that this Box encompasses.
            If None, defaults to the entire window.
        """
        if rect is None:
            rect = cocos.rect.Rect(0, 0, *cocos.director.director.get_window_size())

        super(RectDrawingBox, self).__init__(rect)
        # Dict of rects currently being drawn.
        # Keys are the pyglet integers defining which mouse buttons are pressed.
        self._rects_in_progress: Dict[int, MouseDefinedRect] = {}
        self._rect_displays: Dict[int, cocos.layer.ColorLayer] = {}

        self.drawing_definition: RectDrawingBoxDefinition = definition

    def _update_rect_display(self, buttons: int) -> None:
        """Update the display of the rect during drawing."""
        rect = self._rects_in_progress[buttons].as_rect()
        layer = cocos.layer.ColorLayer(
            *self.drawing_definition.color.as_tuple_alpha(), rect.width, rect.height,
        )
        layer.position = rect.x, rect.y

        if buttons in self._rect_displays.keys():
            self.remove(self._rect_displays[buttons])

        self._rect_displays[buttons] = layer
        self.add(self._rect_displays[buttons])

    def on_press(
        self, box: MouseBox, x: int, y: int, buttons: int, modifiers: int,
    ) -> None:
        """
        Record the start of the rect drawing.

        This records the starting coordinate in local coordinates; the mouse buttons used
        and the keyboard modifiers used.

        Calls the `on_start` callback with the initial definition.
        """
        self._currently_dragging = True
        x, y = self.point_to_local((x, y))
        # End coord starts as the same as the start coord.
        self._rects_in_progress[buttons] = MouseDefinedRect(
            canvas=self,
            buttons=self._currently_pressed,
            modifiers=modifiers,
            start_coord=Point2(x, y),
            end_coord=Point2(x, y),
        )
        self._update_rect_display(buttons)

        if self.drawing_definition.on_start is not None:
            self.drawing_definition.on_start(self._rects_in_progress[buttons])

    def on_release(
        self, box: MouseBox, x: int, y: int, buttons: int, modifiers: int
    ) -> None:
        """
        Record the end of the drawing.

        Records the end coordinates and calls the `on_complete` callback with the final
        definition.
        """
        x, y = self.point_to_local((x, y))
        self._rects_in_progress[buttons].end_coord = Point2(x, y)

        if self.drawing_definition.on_complete is not None:
            self.drawing_definition.on_complete(self._rects_in_progress[buttons])

        del self._rects_in_progress[buttons]
        self.remove(self._rect_displays[buttons])
        del self._rect_displays[buttons]

        # Only stop dragging if every button has been released.
        if self._currently_pressed == 0:
            self._currently_dragging = False

    def on_drag(
        self,
        box: MouseBox,
        x: int,
        y: int,
        dx: int,
        dy: int,
        buttons: int,
        modifiers: int,
    ) -> None:
        """
        Update the definition of the rect being drawn with the latest mouse position.

        Updates the visible rect to the latest rect definition.

        Calls the `on_change` callback with the latest definition.
        """
        x, y = self.point_to_local((x, y))

        # The "buttons" parameter on drag is the bitwise sum of all currently pressed buttons.
        # We already have a record of what's pressed in _rects_in_progress, so just update them all.
        for button, rectdefn in self._rects_in_progress.items():
            rectdefn.end_coord = Point2(x, y)
            self._update_rect_display(button)

            if self.drawing_definition.on_change is not None:
                self.drawing_definition.on_change(rectdefn)
