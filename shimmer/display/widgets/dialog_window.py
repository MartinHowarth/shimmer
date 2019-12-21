"""
Module defining dialogs.

A dialog is a Window with buttons for a multiple choice question.
For example, an "Are you sure" dialog with yes/no answers.
"""

from dataclasses import replace
from functools import update_wrapper
from typing import Sequence, Optional

from .question_definition import (
    MultipleChoiceQuestionDefinition,
    MultipleChoiceResponseCallback,
    QuestionCancelledCallback,
)
from .multiple_choice_buttons import (
    MultipleChoiceButtons,
    MultipleChoiceButtonsDefinition,
)
from .button import ButtonDefinition
from .window import WindowDefinition, Window
from ..components.mouse_box import MouseEventCallable


def callback_with_answer_and_close_window(
    callback: MultipleChoiceResponseCallback, window: Window
) -> MultipleChoiceResponseCallback:
    """Create a callback that closes the window as well as calling the given question callback."""

    def inner(
        currently_selected: Sequence[str], changed_choice: str, choice_state: bool
    ) -> None:
        callback(currently_selected, changed_choice, choice_state)
        window.kill()

    inner = update_wrapper(inner, callback)
    return inner


def create_multiple_choice_question_dialog(
    definition: MultipleChoiceQuestionDefinition,
    on_answer: MultipleChoiceResponseCallback,
    on_cancel: Optional[QuestionCancelledCallback],
) -> Window:
    """
    Create a window containing a multiple choice question.

    :param definition: Definition of the question.
    :param on_answer: Called when an answer is selected.
    :param on_cancel: Called when the window is closed.
    """
    on_close: Optional[MouseEventCallable]

    def cancel_on_close() -> MouseEventCallable:
        """Wrapper around the mouse event callback on close that ignores all the arguments."""

        def inner(*_, **__):
            if on_cancel is not None:
                on_cancel()

        return inner

    if on_cancel is not None:
        on_close = cancel_on_close()
    else:
        on_close = None

    buttons_defn = MultipleChoiceButtonsDefinition(
        question=definition, button=ButtonDefinition(width=80, height=40),
    )
    buttons = MultipleChoiceButtons(buttons_defn)

    margin_x, margin_y = 30, 30
    window_definition = WindowDefinition(
        title=definition.text,
        title_bar_height=None,
        width=buttons.rect.width + margin_x,
        height=buttons.rect.height + margin_y,
        on_close=on_close,
    )
    window = Window(window_definition)

    # Patch the question callback to also close the window when a selection is made.
    buttons.definition = replace(
        buttons.definition,
        question=replace(
            buttons.definition.question,
            on_select=callback_with_answer_and_close_window(on_answer, window),
        ),
    )
    window.add_child_to_body(buttons)

    return window


def create_are_you_sure_dialog(
    on_answer: MultipleChoiceResponseCallback,
    on_cancel: Optional[QuestionCancelledCallback] = None,
) -> Window:
    """
    Create a standard "Are you sure?" dialog.

    Using the `close` button is equivalent to a `No` answer.

    :param on_answer: Method to call when a selection is made.
    :param on_cancel: Method to call if the X button is used instead of answering the question.
    :return: Window containing Yes/No buttons.
    """
    question_defn = MultipleChoiceQuestionDefinition(
        text="Are you sure?",
        choices=["Yes", "No"],
        allow_multiple=False,
        on_cancel=on_cancel,
    )
    return create_multiple_choice_question_dialog(question_defn, on_answer, on_cancel)
