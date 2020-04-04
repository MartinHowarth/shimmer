"""
A set of buttons that users can choose one, or many of.

For example, this can be used to create:
- a radio button
- a "select all that apply" set of buttons
"""

from dataclasses import replace
from typing import Any, Optional

from shimmer.display.widgets.multiple_choice_buttons import (
    MultipleChoiceButtonsDefinition,
    MultipleChoiceButtons,
)
from shimmer.display.widgets.question_definition import OnQuestionChangeCallback
from shimmer.display.widgets.window import Window
from .base_dialog_window import create_base_dialog_window


def callback_with_answer_and_close_window(
    on_change: Optional[OnQuestionChangeCallback], window: Window
) -> OnQuestionChangeCallback:
    """Create a callback that calls both the on_change and window.close methods."""

    def inner(answer: Any) -> None:
        if on_change is not None:
            on_change(answer)
        # Use kill rather than close because we don't want to call the on_cancel that using
        # the close button would do.
        window.kill()

    return inner


def create_multiple_choice_question_dialog(
    definition: MultipleChoiceButtonsDefinition,
) -> Window:
    """
    Create a window containing a multiple choice question.

    If the question allows multiple answers, a submit button will be shown that closes the window.
    The submit button doe not call any additional callback as each answer choice will have called
    back already.

    If confirmation is not required, the window will close as soon as an option is chosen.
    Otherwise, "Ok" and "Cancel" buttons will be added.

    :param definition: Definition of the question.
    """
    window = create_base_dialog_window(definition.question)

    if not definition.question.confirmation_required:
        # If confirmation is not required then close the window when any answer is selected.
        definition = replace(
            definition,
            question=replace(
                definition.question,
                on_change=callback_with_answer_and_close_window(
                    definition.question.on_change, window
                ),
            ),
        )

    buttons = MultipleChoiceButtons(definition)
    window.add_child_to_body(buttons)

    return window
