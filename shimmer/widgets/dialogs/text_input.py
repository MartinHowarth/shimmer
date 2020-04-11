"""Module aiding the creation of text input dialogs."""

from dataclasses import replace

from .base_dialog_window import create_base_dialog_window
from ..question_definition import TextInputQuestionDefinition
from ..text_box import EditableTextBox
from ..window import Window


def create_text_input_dialog(definition: TextInputQuestionDefinition) -> Window:
    """Create a text input dialog window."""
    window = create_base_dialog_window(definition)
    text_box_definition = replace(
        definition.text_box_definition, on_change=definition.on_change
    )
    text_box = EditableTextBox(text_box_definition)
    window.add_child_to_body(text_box)
    return window
