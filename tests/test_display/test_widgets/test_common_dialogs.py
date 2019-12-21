"""Tests for the common dialog windows.."""

from shimmer.display.widgets.dialog_window import create_are_you_sure_dialog


def test_are_you_sure_dialog(run_gui, multi_choice_result_display):
    """
    3 dialogs asking "Are you sure?" should be shown with Yes/No answers.

    The Yes/No and close button should set the placeholder text appropriately.
    """
    text_box, update_text_box = multi_choice_result_display

    def on_cancel():
        text_box.set_text("Cancelled")

    dialog = create_are_you_sure_dialog(update_text_box, on_cancel)
    dialog1 = create_are_you_sure_dialog(update_text_box, on_cancel)
    dialog1.position = 100, 100
    dialog2 = create_are_you_sure_dialog(update_text_box, on_cancel)
    dialog2.position = 200, 200
    assert run_gui(test_are_you_sure_dialog, dialog, dialog1, dialog2, text_box)
