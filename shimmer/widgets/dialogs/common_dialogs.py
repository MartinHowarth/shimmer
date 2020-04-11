"""
Module defining common dialogs.

A dialog is a Window with buttons for a multiple choice question.
For example, an "Are you sure" dialog with yes/no answers.
"""

from typing import Optional

from shimmer.widgets.dialogs.multiple_choice import (
    create_multiple_choice_question_dialog,
    MultipleChoiceButtonsDefinition,
)
from shimmer.widgets.question_definition import (
    MultipleChoiceQuestionDefinition,
    NoArgumentsCallback,
    OnQuestionChangeCallback,
)
from shimmer.widgets.window import Window


def create_are_you_sure_dialog(
    on_answer: OnQuestionChangeCallback,
    on_cancel: Optional[NoArgumentsCallback] = None,
) -> Window:
    """
    Create a standard "Are you sure?" dialog.

    Using the `close` button is equivalent to a `No` answer.

    :param on_answer: Method to call when a selection is made.
    :param on_cancel: Method to call if the X button is used instead of answering the question.
    :return: Window containing Yes/No buttons.
    """
    return create_multiple_choice_question_dialog(
        MultipleChoiceButtonsDefinition(
            question=MultipleChoiceQuestionDefinition(
                text="Are you sure?",
                choices=["Yes", "No"],
                on_change=on_answer,
                on_cancel=on_cancel,
                allow_multiple=False,
            )
        )
    )
