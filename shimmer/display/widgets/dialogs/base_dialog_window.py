"""Base definition and creation of dialog windows."""

import logging
from typing import Optional

from pyglet.window import key

from shimmer.display.components.box_layout import BoxRow
from shimmer.display.components.mouse_box import MouseClickEventCallable
from shimmer.display.keyboard import KeyboardHandler, KeyboardHandlerDefinition
from shimmer.display.widgets.button import ButtonDefinition, Button
from shimmer.display.widgets.question_definition import QuestionDefinition
from shimmer.display.widgets.window import Window, WindowDefinition

log = logging.getLogger(__name__)


def create_base_dialog_window(definition: QuestionDefinition) -> Window:
    """
    Create a window containing a multiple choice question.

    If the question allows multiple answers, a submit button will be shown that closes the window.
    The submit button does not call any additional callback as each answer choice will have called
    back already.

    If confirmation is not required, the window will close as soon as an option is chosen.
    Otherwise, "Ok" and "Cancel" buttons will be added.

    :param definition: Definition of the question.
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

    window_definition = WindowDefinition(title=definition.text, on_close=on_close,)
    window = Window(window_definition)

    if definition.confirmation_required:
        # Create "Ok" and "Cancel" buttons
        # The "Ok" button calls the `on_confirm` callback with the current selection.
        # The Cancel button is equivalent to clicking the "X".
        def on_ok(*_, **__):
            if definition.on_confirm is not None:
                definition.on_confirm()
            window.close()

        def on_cancel(*_, **__):
            # We set the window to call the cancel callback on close above,
            # so just close the window here.
            window.close()

        ok_button = Button(ButtonDefinition(text="Ok", on_press=on_ok))
        cancel_button = Button(ButtonDefinition(text="Cancel", on_press=on_cancel))
        confirmation_buttons = BoxRow(boxes=(ok_button, cancel_button))

        # Add keyboard handler to make Enter/Esc hit Ok/Cancel respectively.
        keyboard_handler_defn = KeyboardHandlerDefinition(
            focus_required=False, logging_name="dialog_enter_escape",
        )
        keyboard_handler_defn.add_keyboard_action_simple(
            key=key.ENTER, action=ok_button.on_keyboard_select_press
        )
        keyboard_handler_defn.add_keyboard_action_simple(
            key=key.NUM_ENTER, action=ok_button.on_keyboard_select_press
        )
        keyboard_handler_defn.add_keyboard_action_simple(
            key=key.ESCAPE, action=cancel_button.on_keyboard_select_press,
        )
        keyboard_handler = KeyboardHandler(keyboard_handler_defn)

        confirmation_buttons.add(keyboard_handler)

        window.add_child_to_body(confirmation_buttons)

    return window
