"""Common fixtures to aid testing of widgets."""

from typing import Tuple, Callable, Any

import pytest

from shimmer.widgets.question_definition import OnQuestionChangeCallback
from shimmer.widgets.text_box import TextBox


@pytest.fixture
def question_result_display(
    updatable_text_box: Tuple[TextBox, Callable[[str], None]],
) -> Tuple[TextBox, OnQuestionChangeCallback]:
    """
    Fixture to create a text box whose text can be updated using the given callback.

    Will show the confirmed result of a question..
    """
    text_box, update_text_box = updatable_text_box

    def update_text_box_with_multi_question(answer: Any) -> None:
        nonlocal text_box
        update_text_box("You selected: " + str(answer))

    return text_box, update_text_box_with_multi_question
