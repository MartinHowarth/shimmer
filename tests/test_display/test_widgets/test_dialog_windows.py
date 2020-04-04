"""Tests for the common dialog windows."""

from shimmer.display.widgets.dialogs.common_dialogs import create_are_you_sure_dialog
from shimmer.display.widgets.dialogs.multiple_choice import (
    create_multiple_choice_question_dialog,
)
from shimmer.display.widgets.dialogs.text_input import (
    create_text_input_dialog,
    TextInputQuestionDefinition,
)
from shimmer.display.widgets.multiple_choice_buttons import (
    MultipleChoiceButtonsDefinition,
)
from shimmer.display.widgets.question_definition import MultipleChoiceQuestionDefinition


def test_are_you_sure_dialog(run_gui, question_result_display):
    """
    3 dialogs asking "Are you sure?" should be shown with Yes/No answers.

    The Yes/No and close button should set the placeholder text appropriately.
    """
    text_box, update_text_box = question_result_display

    def on_cancel():
        text_box.set_text("Cancelled")

    dialog = create_are_you_sure_dialog(update_text_box, on_cancel)
    dialog1 = create_are_you_sure_dialog(update_text_box, on_cancel)
    dialog1.position = 100, 100
    dialog2 = create_are_you_sure_dialog(update_text_box, on_cancel)
    dialog2.position = 200, 200
    assert run_gui(test_are_you_sure_dialog, dialog, dialog1, dialog2, text_box)


def test_dialog_requiring_confirmation(run_gui, question_result_display):
    """
    A dialog window should be shown with a multiple choice question.

    The placeholder text should update only when the "Ok" button is pressed.
    """
    text_box, update_text_box = question_result_display

    current_answer = None

    def on_change(answer):
        nonlocal current_answer
        current_answer = answer

    def on_confirm():
        nonlocal current_answer
        update_text_box(current_answer)

    question_definition = MultipleChoiceButtonsDefinition(
        question=MultipleChoiceQuestionDefinition(
            text="You must choose!",
            on_change=on_change,
            on_confirm=on_confirm,
            choices=[str(i) for i in range(4)],
            allow_multiple=True,
        )
    )

    dialog = create_multiple_choice_question_dialog(question_definition)
    assert run_gui(test_dialog_requiring_confirmation, dialog, text_box)


def test_text_input_dialog(run_gui, question_result_display):
    """
    A dialog window should be shown with an editable text box.

    The placeholder text should update to show exactly what is entered into the text box.
    """
    text_box, update_text_box = question_result_display

    current_answer = None

    def on_change(answer):
        nonlocal current_answer
        current_answer = answer

    def on_confirm():
        nonlocal current_answer
        update_text_box(current_answer)

    question_definition = TextInputQuestionDefinition(
        text="What is your name?", on_change=on_change, on_confirm=on_confirm,
    )

    dialog = create_text_input_dialog(question_definition)
    assert run_gui(test_text_input_dialog, dialog, text_box)
