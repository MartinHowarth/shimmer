"""Test visual text boxes."""

from dataclasses import replace

import pytest

from shimmer.alignment import HorizontalAlignment
from shimmer.components.font import Calibri, ComicSans
from shimmer.data_structures import Grey
from shimmer.widgets.text_box import (
    TextBox,
    TextBoxDefinition,
    EditableTextBox,
    EditableTextBoxDefinition,
)


@pytest.fixture
def dummy_text_box_definition():
    """Common definition of a TextBox for use in the tests."""
    return TextBoxDefinition(
        text="This is a sample sentence. " * 10,
        font=Calibri,
        background_color=Grey,
        width=300,
    )


def test_text_box_basic(run_gui):
    """A text box should be shown with a tightly matching background."""
    text_box = TextBox(
        TextBoxDefinition(text="This is a sample sentence.", background_color=Grey)
    )
    assert run_gui(test_text_box_basic, text_box)


def test_text_box_left_justified(run_gui, dummy_text_box_definition):
    """A text box should be shown with left-justified text and wrapped text."""
    dummy_text_box_definition = replace(
        dummy_text_box_definition, justification=HorizontalAlignment.left,
    )
    text_box = TextBox(dummy_text_box_definition)
    assert run_gui(test_text_box_left_justified, text_box)


def test_text_box_center_justified(run_gui, dummy_text_box_definition):
    """A text box should be shown with center-justified text and wrapped text."""
    dummy_text_box_definition = replace(
        dummy_text_box_definition, justification=HorizontalAlignment.center,
    )
    text_box = TextBox(dummy_text_box_definition)
    assert run_gui(test_text_box_center_justified, text_box)


def test_text_box_right_justified(run_gui, dummy_text_box_definition):
    """A text box should be shown with right-justified text and wrapped text."""
    dummy_text_box_definition = replace(
        dummy_text_box_definition, justification=HorizontalAlignment.right,
    )
    text_box = TextBox(dummy_text_box_definition)
    assert run_gui(test_text_box_right_justified, text_box)


def test_text_box_no_multline(run_gui):
    """A text box should be shown with no wrapped text (i.e. on a single line)."""
    defn = TextBoxDefinition(
        text="This is a sample sentence. " * 10,
        font=ComicSans,
        width=None,
        background_color=Grey,
    )
    text_box = TextBox(defn)
    assert run_gui(test_text_box_no_multline, text_box)


def test_editable_text_box(run_gui):
    """A text box should be shown and the text should be editable on a single line."""
    defn = EditableTextBoxDefinition(text="Edit me!", width=300, background_color=Grey)
    text_box = EditableTextBox(defn)
    assert run_gui(test_editable_text_box, text_box)


def test_multiple_text_boxes(run_gui):
    """Multiple single line text boxes should be shown and each should be individually editable."""
    defn = EditableTextBoxDefinition(text="Edit me!", width=300, background_color=Grey)
    text_boxes = []
    for i in range(3):
        text_box = EditableTextBox(defn)
        text_box.position = 0, i * 50
        text_boxes.append(text_box)

    assert run_gui(test_multiple_text_boxes, *text_boxes)


def test_editable_text_box_multiline(run_gui):
    """A text box should be shown and the text should be editable with multiline text."""
    defn = EditableTextBoxDefinition(
        text="Edit me!", width=300, height=100, background_color=Grey, multiline=True,
    )
    text_box = EditableTextBox(defn)
    assert run_gui(test_editable_text_box_multiline, text_box)
