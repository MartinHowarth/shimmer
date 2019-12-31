"""
Module defining dialogs.

A dialog is a Window with buttons for a multiple choice question.
For example, an "Are you sure" dialog with yes/no answers.
"""

from dataclasses import replace
from functools import update_wrapper
from typing import Optional, Set

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
from ..components.mouse_box import MouseClickEventCallable


AreYouSure = MultipleChoiceQuestionDefinition(
    text="Are you sure?", choices=["Yes", "No"], allow_multiple=False,
)


def callback_with_answer_and_close_window(
    callback: MultipleChoiceResponseCallback, window: Window
) -> MultipleChoiceResponseCallback:
    """Create a callback that closes the window as well as calling the given question callback."""

    def inner(
        currently_selected: Set[str], changed_choice: str, choice_state: bool
    ) -> None:
        callback(currently_selected, changed_choice, choice_state)
        window.kill()

    inner = update_wrapper(inner, callback)
    return inner


def create_multiple_choice_question_dialog(
    definition: MultipleChoiceQuestionDefinition,
    on_answer: MultipleChoiceResponseCallback,
) -> Window:
    """
    Create a window containing a multiple choice question.

    If the question allows multiple answers, a submit button will be shown that closes the window.
    The submit button doe not call any additional callback as each answer choice will have called
    back already.

    If only a single answer is allowed, the window will close as soon as an option is chosen.

    :param definition: Definition of the question.
    :param on_answer: Called when an answer is selected.
    """
    on_close: Optional[MouseClickEventCallable]

    def cancel_on_close() -> MouseClickEventCallable:
        """Wrapper around the mouse event callback on close that ignores all the arguments."""

        def inner(*_, **__):
            if definition.on_cancel is not None:
                definition.on_cancel()

        return inner

    if definition.on_cancel is not None:
        on_close = cancel_on_close()
    else:
        on_close = None

    buttons_defn = MultipleChoiceButtonsDefinition(
        question=definition, button=ButtonDefinition(width=80, height=40),
    )
    buttons = MultipleChoiceButtons(buttons_defn)

    margin_x, margin_y = 15, 15
    window_definition = WindowDefinition(
        title=definition.text,
        width=buttons.rect.width + 2 * margin_x,
        body_height=buttons.rect.height + 2 * margin_y,
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
    question_defn = replace(AreYouSure, on_cancel=on_cancel)
    return create_multiple_choice_question_dialog(question_defn, on_answer)
