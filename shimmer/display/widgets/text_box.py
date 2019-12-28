"""A Box that automatically sets its size to fit the given text."""

import cocos

from dataclasses import dataclass, replace
from typing import Optional

from ..components.box import Box, BoxDefinition
from ..data_structures import (
    Color,
    LabelDefinition,
)


@dataclass(frozen=True)
class TextBoxDefinition(BoxDefinition):
    """Definition of a text box."""

    label: LabelDefinition = LabelDefinition(text="")
    background_color: Color = Color(40, 40, 40)


class TextBox(Box):
    """A rectangle containing text with a background color."""

    def __init__(self, definition: TextBoxDefinition):
        """Create a new TextBox."""
        super(TextBox, self).__init__()
        self.definition: TextBoxDefinition = definition
        self._label: Optional[cocos.text.Label] = None
        self._update_label()

    @property
    def text(self) -> str:
        """Get the current text in the Box."""
        return self.definition.label.text

    @text.setter
    def text(self, value: str) -> None:
        """Set the text of the box and update the display."""
        self.set_text(value)

    def set_text(self, text: str) -> None:
        """Set the text of the box and update the display."""
        new_label = replace(self.definition.label, text=text)
        self.definition = replace(self.definition, label=new_label)
        self._update_label()

    def _update_label(self):
        """Update the text of this Box."""
        if self._label is not None:
            self.remove(self._label)

        self._label = cocos.text.Label(**self.definition.label.to_pyglet_label_kwargs())
        self.add(self._label)
        # Use "or 1" to avoid cocos default of 0 meaning entire window.
        self.set_size(
            self._label.element.content_width or 1,
            self._label.element.content_height or 1,
        )
