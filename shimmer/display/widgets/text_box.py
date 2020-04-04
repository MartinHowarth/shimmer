"""A Box that automatically sets its size to fit the given text."""

import logging
from dataclasses import dataclass, replace
from typing import Optional, Dict, Any, Callable

import pyglet
from pyglet import gl

import cocos
from ..alignment import HorizontalAlignment, LeftBottom
from ..components.box import Box, bounding_rect_of_rects
from ..components.focus import KeyboardFocusBox, FocusBoxDefinition, make_focusable
from ..components.font import FontDefinition, Calibri
from ..components.mouse_box import (
    MouseBox,
    MouseBoxDefinition,
    EVENT_UNHANDLED,
    EVENT_HANDLED,
)
from ..data_structures import White, Black, Color
from ..keyboard import KeyboardHandlerDefinition, KeyboardHandler

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class TextBoxDefinition(MouseBoxDefinition):
    """
    Definition of a Box containing text. All parameters match pyglet Label parameters.

    Note that the parameters are for the pyglet text layout, rather than the cocos Label.
    The pyglet text layout is a property of the Label called `element.

    Pay attention in particular to `width` and `height`. For this Box they define the size of the
    pyglet text label as well as the surrounding Box. That means that a fixed-size TextBox will
    be very difficult to get exactly centered text. Instead you should consider creating a
    dynamically sized TextBox (i.e. width=None, height=None) and centering that inside another Box.
    """

    text: str = ""
    font: FontDefinition = Calibri

    # Maximum width of the label. Text is wrapped to fit within this width.
    # Set to None to force single line text of arbitrary width.
    width: Optional[int] = None

    # Maximum height of the label. If None, height of the box is set as needed based on
    # the length of text and whether it is multiline or not.
    height: Optional[int] = None

    # Justification the text. E.g. do multiple lines align on the left, center or right?
    justification: HorizontalAlignment = HorizontalAlignment.left

    # Used to override default multiline behaviour which is based on whether `width` is set or not.
    # Use `is_multiline()` to determine whether to use multiline or not.
    multiline: Optional[bool] = None

    def is_multiline(self) -> bool:
        """Determine whether this label should be multiline or not if user hasn't specified."""
        if self.multiline is None:
            return self.width is not None
        return self.multiline

    def to_pyglet_label_kwargs(self) -> Dict[str, Any]:
        """Convert this definition into cocos/pyglet compatible kwargs."""
        return {
            "text": self.text,
            "width": self.width,
            "height": self.height,
            "align": self.justification.value,
            "anchor_x": LeftBottom.x.value,
            "anchor_y": LeftBottom.y.value,
            "multiline": self.is_multiline(),
            **self.font.to_pyglet_label_kwargs(),
        }


class TextBox(MouseBox):
    """
    A rectangle containing text with an optional background color.

    The size of the text box always matches the size of the text (i.e. the size of the
    underlying pyglet Label).

    A TextBox can be thought of as a Box which contains a pyglet Label.
    """

    def __init__(self, definition: TextBoxDefinition):
        """Create a new TextBox."""
        self._label: Optional[cocos.text.Label] = None
        super(TextBox, self).__init__(definition)
        self.definition: TextBoxDefinition = definition
        self._update_label()

    @property
    def text(self) -> str:
        """Get the current text in the Box."""
        return self.definition.text

    @text.setter
    def text(self, value: str) -> None:
        """Set the text of the box and update the display."""
        self.set_text(value)

    def set_text(self, text: str) -> None:
        """Set the text of the box and update the display."""
        self.definition = replace(self.definition, text=text)
        self._update_label()

    def _update_label(self):
        """Update the text of this Box."""
        if self._label is not None:
            self.remove(self._label)

        self._label = cocos.text.Label(**self.definition.to_pyglet_label_kwargs())

        if self.definition.is_dynamic_sized:
            width = self._label.element.content_width
            height = self._label.element.content_height
        else:
            width = self.definition.width
            height = self.definition.height

        # Set the position of the label to the center of this Box.
        # Only attempt to calculate this if the text is not empty, otherwise pyglet gets sad.
        if self.definition.text:
            self._label.position = LeftBottom.get_coord_in_rect(width, height)
        self.add(self._label)

    def bounding_rect_of_children(self) -> cocos.rect.Rect:
        """Get the rect containing all of this boxes children and also the pyglet label."""
        rect = super(TextBox, self).bounding_rect_of_children()
        if self._label is None:
            return rect

        # Pyglet labels are not Boxes, so have to manually calculate the rect of this Box.
        if self.definition.is_dynamic_sized:
            self_rect = cocos.rect.Rect(
                0,
                0,
                self._label.element.content_width,
                self._label.element.content_height,
            )
        else:
            self_rect = self.rect
        return bounding_rect_of_rects((rect, self_rect))


@dataclass(frozen=True)
class EditableTextBoxDefinition(TextBoxDefinition):
    """
    Definition of a user-editable text box.

    If `height` is None, then the height of the font is used.
    """

    width: int = 300
    height: Optional[int] = None
    multiline: bool = False
    background_color: Color = White
    font: FontDefinition = FontDefinition("calibri", 16, color=Black)
    on_change: Optional[Callable[[str], None]] = None

    @property
    def actual_height(self) -> int:
        """
        Height of the text box to create.

        Equal to `height` if given, otherwise will be the height required for a single line of text.
        """
        return self.height if self.height is not None else self.font.height


class EditableTextBox(MouseBox):
    """
    A text box whose text can be edited by the user.

    The size of this box matches the defined size, unlike TextBox (which matches the
    text size).
    """

    def __init__(self, definition: EditableTextBoxDefinition):
        """Create a new EditableTextBox."""
        definition = replace(
            definition,
            height=definition.actual_height,
            on_press=self.enter_edit_mode,
            on_release=self.exit_drag_mode,
            on_hover=self.set_text_cursor,
            on_unhover=self.set_normal_cursor,
            on_drag=self.highlight_text_on_drag,
        )
        super(EditableTextBox, self).__init__(definition)
        self.definition: EditableTextBoxDefinition = definition
        self.batch = pyglet.graphics.Batch()

        document = pyglet.text.decode_attributed(self.definition.text)
        self._layout = pyglet.text.layout.IncrementalTextLayout(
            document,
            self.definition.width,
            self.definition.actual_height,
            multiline=self.definition.multiline,
            dpi=self.definition.font.dpi,
            batch=self.batch,
        )
        self._caret: pyglet.text.caret.Caret = pyglet.text.caret.Caret(
            self._layout, batch=self.batch
        )
        self._hide_caret()
        self._text_cursor = cocos.director.director.window.get_system_mouse_cursor(
            "text"
        )
        self._keyboard_handler = KeyboardHandler(
            KeyboardHandlerDefinition(
                on_text=self.on_text,
                on_text_motion=self._caret.on_text_motion,
                on_text_motion_select=self._caret.on_text_motion_select,
                logging_name="text_box",
            )
        )
        self.add(self._keyboard_handler)

        self.focus_box = make_focusable(
            self,
            FocusBoxDefinition(
                on_take_focus=self.take_focus, on_lose_focus=self.lose_focus,
            ),
            focus_type=KeyboardFocusBox,
        )

    @property
    def text(self) -> str:
        """The current text in the text box."""
        return self._layout.document.text

    def on_text(self, text: str) -> Optional[bool]:
        """Called when the user enters text into the text box."""
        if self.definition.on_change is not None:
            self.definition.on_change(self.text)
        return self._caret.on_text(text)

    def take_focus(self):
        """Start capturing keyboard events."""
        self._show_caret()
        self._keyboard_handler.set_focused()

    def lose_focus(self):
        """Stop capturing keyboard events."""
        self._hide_caret()
        self._keyboard_handler.set_unfocused()

    def draw(self):
        """Draw the pyglet children."""
        gl.glPushMatrix()
        self.transform()
        self.batch.draw()
        gl.glPopMatrix()

    def _show_caret(self):
        """Make the text caret visible."""
        self._caret.visible = True
        self._caret.mark = 0
        self._caret.position = len(self._layout.document.text)

    def _hide_caret(self):
        """Make the text caret invisible."""
        self._caret.visible = False
        self._caret.mark = 0
        self._caret.position = 0

    def enter_edit_mode(
        self, box: "EditableTextBox", x: int, y: int, buttons: int, modifiers: int
    ) -> Optional[bool]:
        """Enter edit mode for this EditableTextBox."""
        x, y = self.point_to_local((x, y))
        self.start_dragging(box, x, y, buttons, modifiers)
        self._caret.on_mouse_press(x, y, buttons, modifiers)
        return EVENT_HANDLED

    def exit_drag_mode(
        self, box: "EditableTextBox", x: int, y: int, buttons: int, modifiers: int
    ) -> Optional[bool]:
        """Stop dragging - i.e. stop highlighting text."""
        self.stop_dragging(box, x, y, buttons, modifiers)
        return EVENT_HANDLED

    def set_text_cursor(
        self, box: "EditableTextBox", x: int, y: int, dx: int, dy: int
    ) -> Optional[bool]:
        """Make the mouse cursor look like the system text cursor."""
        cocos.director.director.window.set_mouse_cursor(self._text_cursor)
        return EVENT_UNHANDLED

    def set_normal_cursor(
        self, box: "EditableTextBox", x: int, y: int, dx: int, dy: int
    ) -> Optional[bool]:
        """Make the mouse cursor look like the normal system cursor."""
        cocos.director.director.window.set_mouse_cursor(None)
        return EVENT_UNHANDLED

    def highlight_text_on_drag(
        self,
        box: "EditableTextBox",
        x: int,
        y: int,
        dx: int,
        dy: int,
        buttons: int,
        modifiers: int,
    ) -> Optional[bool]:
        """Highlight the text that has been dragged over by the mouse."""
        x, y = self.point_to_local((x, y))
        self._caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        return EVENT_HANDLED


def add_centralised_text(
    box: Box, text: str, text_box_definition: Optional[TextBoxDefinition] = None
) -> None:
    """Add the given text to the center of the given Box."""
    if text_box_definition is None:
        text_box_definition = TextBoxDefinition(text=text)
    else:
        text_box_definition = replace(text_box_definition, text=text)

    text_box = TextBox(text_box_definition)
    box.add(text_box)
    text_box.align_anchor_with_other_anchor(box)
