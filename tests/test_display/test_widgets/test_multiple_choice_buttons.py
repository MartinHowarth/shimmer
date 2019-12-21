"""Test the multiple choice button widget."""

import pytest

from dataclasses import replace
from typing import Tuple

from shimmer.display.data_structures import Color
from shimmer.display.widgets.button import ButtonDefinition
from shimmer.display.widgets.multiple_choice_buttons import (
    MultipleChoiceButtonsDefinition,
    MultipleChoiceButtons,
)
from shimmer.display.widgets.question_definition import (
    MultipleChoiceQuestionDefinition,
    MultipleChoiceResponseCallback,
)
from shimmer.display.widgets.text_box import TextBox


@pytest.fixture
def dummy_button_definition() -> ButtonDefinition:
    """Common button definition for use in these tests."""
    return ButtonDefinition(width=100, height=100, depressed_color=Color(0, 80, 255))


@pytest.fixture
def dummy_multi_choice(
    multi_choice_result_display: Tuple[TextBox, MultipleChoiceResponseCallback],
) -> Tuple[TextBox, MultipleChoiceQuestionDefinition]:
    """
    Common multiple choice question definition to use in this test.

    Also returns a text box that updates to shown the current question response.
    """
    text_box, update_text_box = multi_choice_result_display

    question_defn = MultipleChoiceQuestionDefinition(
        text="", choices=["1", "2", "3"], on_select=update_text_box
    )
    return text_box, question_defn


def test_multiple_choice_buttons(run_gui, dummy_button_definition, dummy_multi_choice):
    """3 buttons should be shown and only one should be selectable at a time."""
    text_box, question_defn = dummy_multi_choice
    multi = MultipleChoiceButtons(
        MultipleChoiceButtonsDefinition(
            question=question_defn, button=dummy_button_definition,
        )
    )
    assert run_gui(test_multiple_choice_buttons, multi, text_box)


def test_multiple_choice_buttons_multiple_selectable(
    run_gui, dummy_button_definition, dummy_multi_choice
):
    """3 buttons should be shown and they should all be individually selectable."""
    text_box, question_defn = dummy_multi_choice
    question_defn = replace(question_defn, allow_multiple=True,)

    multi = MultipleChoiceButtons(
        MultipleChoiceButtonsDefinition(
            question=question_defn, button=dummy_button_definition,
        )
    )
    assert run_gui(test_multiple_choice_buttons_multiple_selectable, multi, text_box)


def test_multiple_choice_with_defaults(
    subtests, run_gui, dummy_button_definition, dummy_multi_choice
):
    """3 buttons should be shown and the "2" option should be pre-selected."""
    text_box, base_defn = dummy_multi_choice

    with subtests.test(
        "Multiple defaults without `allow_multiple` should not be allowed."
    ):
        with pytest.raises(ValueError):
            replace(base_defn, defaults={"2", "3"})

    with subtests.test("Default that is not a valid choice is rejected."):
        with pytest.raises(ValueError):
            replace(base_defn, defaults={"4"})

    question_defn = replace(base_defn, defaults={"2"})

    multi = MultipleChoiceButtons(
        MultipleChoiceButtonsDefinition(
            question=question_defn, button=dummy_button_definition,
        )
    )
    assert run_gui(test_multiple_choice_with_defaults, multi, text_box)
