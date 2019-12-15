"""Test visual text boxes."""

import pytest

from shimmer.display.widgets.text_box import TextBox, TextBoxDefinition
from shimmer.display.data_structures import (
    Calibri,
    ComicSans,
    LabelDefinition,
    HorizontalAlignment,
)


@pytest.fixture
def dummy_text_box_definition():
    """Common definition of a TextBox for use in the tests."""
    return TextBoxDefinition(
        label=LabelDefinition(text="This is a sample sentence. " * 10, font=Calibri)
    )


def test_text_box(run_gui, dummy_text_box_definition):
    """A text box should be shown with left-aligned text and wrapped text."""
    text_box = TextBox(dummy_text_box_definition)
    assert run_gui(test_text_box, text_box)


def test_text_box_center_align(run_gui, dummy_text_box_definition):
    """A text box should be shown with center-aligned text and wrapped text."""
    dummy_text_box_definition.label.align = HorizontalAlignment.center
    text_box = TextBox(dummy_text_box_definition)
    assert run_gui(test_text_box, text_box)


def test_text_box_right_align(run_gui, dummy_text_box_definition):
    """A text box should be shown with right-aligned text and wrapped text."""
    dummy_text_box_definition.label.align = HorizontalAlignment.right
    text_box = TextBox(dummy_text_box_definition)
    assert run_gui(test_text_box, text_box)


def test_text_box_no_multline(run_gui, dummy_text_box_definition):
    """
    A text box should be shown with no wrapped text (i.e. on a single line).
    """
    defn = TextBoxDefinition(
        label=LabelDefinition(
            text="This is a sample sentence. " * 10, font=ComicSans, width=None
        ),
    )
    text_box = TextBox(defn)
    assert run_gui(test_text_box, text_box)
