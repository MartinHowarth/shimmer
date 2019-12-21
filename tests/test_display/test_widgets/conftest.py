"""Common fixtures to aid testing of widgets."""

import pytest

from typing import Tuple, Sequence, Callable

from shimmer.display.widgets.question_definition import MultipleChoiceResponseCallback
from shimmer.display.widgets.text_box import TextBox, TextBoxDefinition, LabelDefinition


@pytest.fixture
def updatable_text_box() -> Tuple[TextBox, Callable[[str], None]]:
    """Fixture to create a text box whose text can be updated using the given callback."""
    text_box = TextBox(TextBoxDefinition(LabelDefinition("<placeholder>")))
    text_box.position = 0, 300

    def update_text_box(text: str) -> None:
        nonlocal text_box
        text_box.set_text(text)

    return text_box, update_text_box


@pytest.fixture
def multi_choice_result_display(
    updatable_text_box: Tuple[TextBox, Callable[[str], None]],
) -> Tuple[TextBox, MultipleChoiceResponseCallback]:
    """
    Fixture to create a text box whose text can be updated using the given callback.

    Will show the current selected options of a multiple choice question.
    """
    text_box, update_text_box = updatable_text_box

    def update_text_box_with_multi_question(
        currently_selected: Sequence[str], changed_choice: str, choice_state: bool
    ) -> None:
        nonlocal text_box
        selected_str = ", ".join(currently_selected)
        update_text_box("You selected: " + selected_str)

    return text_box, update_text_box_with_multi_question
