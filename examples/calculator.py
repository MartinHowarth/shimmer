"""Example of a simple calculator written using shimmer."""

from typing import Optional, List, Callable

from pyglet.window import key

import cocos
from shimmer.components.box_layout import create_box_layout, BoxGridDefinition
from shimmer.components.font import FontDefinition
from shimmer.data_structures import White, Black
from shimmer.keyboard import (
    KeyboardActionDefinition,
    KeyboardHandlerDefinition,
    KeyboardHandler,
    ChordDefinition,
)
from shimmer.widgets.button import ButtonDefinition, Button
from shimmer.widgets.text_box import TextBoxDefinition, TextBox
from shimmer.widgets.window import WindowDefinition, Window


class Calculator(Window):
    """A simple calculator."""

    symbol_layout = [
        ["7", "8", "9", "+"],
        ["4", "5", "6", "-"],
        ["1", "2", "3", "/"],
        ["C", "0", "=", "*"],
    ]
    layout_definition = BoxGridDefinition(num_columns=4, num_rows=4)

    def __init__(self):
        """Create a Calculator."""
        definition = WindowDefinition(title="Calculator", title_bar_height=None)
        super(Calculator, self).__init__(definition)
        self.calculation: str = ""
        self.result: Optional[str] = None

        # Create all the calculator buttons.
        self.buttons = self.create_buttons()

        # Arrange them into a grid layout.
        self.button_layout = create_box_layout(self.layout_definition, self.buttons)

        # Create the calculator display
        self.text_box = TextBox(
            TextBoxDefinition(
                width=self.button_layout.rect.width,
                height=30,
                background_color=White,
                font=FontDefinition("calibri", 16, color=Black),
            )
        )

        # Create a keyboard handler and add it to this node so that it responds to keyboard events.
        self.keyboard_handler = KeyboardHandler(self.create_keymap())
        self.add(self.keyboard_handler)

        # Add the display and the buttons to the Window body with sensible alignment.
        self.add_child_to_body(self.button_layout)
        self.add_child_to_body(self.text_box)

    def create_buttons(self) -> List[Button]:
        """Create a button for each of the defined symbols in the symbol layout."""
        buttons = []
        # Reversed order because box layouts build from bottom-left.
        for row in reversed(self.symbol_layout):
            for symbol in row:
                buttons.append(self.make_button_with_symbol(symbol))

        return buttons

    def make_button_with_symbol(self, symbol: str) -> Button:
        """Create a single button that will call `on_symbol_press` when pressed."""

        def callback(*_, **__):
            """Callback when clicked. Ignore mouse event arguments as we don't need them."""
            nonlocal symbol
            self.on_button_press(symbol)
            return True

        return Button(
            ButtonDefinition(
                text=symbol,
                on_press=callback,
                width=50,
                height=50,
                keyboard_shortcut=symbol,
            )
        )

    def on_button_press(self, symbol: str) -> None:
        """Handle any button press by updating the display and calculating results."""
        # If we have a previous result, reset the calculation to start with that.
        if self.result is not None:
            self.calculation = self.result
            self.result = None

        if symbol == "=":
            try:
                exec(f"self.result = str({self.calculation})")
            except Exception:
                self.result = "Err"
            self.calculation += symbol
            self.calculation += self.result  # type: ignore # Ignore type because of use of `exec`.
        elif symbol == "C":
            self.calculation = ""
            self.result = None
        else:
            self.calculation += symbol
        self.update_display()

    def update_display(self):
        """Update the calculator display."""
        self.text_box.text = self.calculation

    def create_keymap(self) -> KeyboardHandlerDefinition:
        """
        Create an additional keymap for this calculator.

        Keyboard definitions on each button are already handled, this adds control
        for extra keyboard presses that translate onto calculator events such
        as ENTER instead of "=".
        """

        def on_key_press(symbol: str) -> Callable:
            """Callback for handling keyboard events."""

            def inner() -> bool:
                self.on_button_press(symbol)
                # Return True to mark the keyboard event as handled.
                return True

            return inner

        keymap = KeyboardHandlerDefinition()

        # Make the ENTER keys also trigger equals.
        keymap.add_keyboard_action(
            KeyboardActionDefinition(
                chords=[ChordDefinition(key.ENTER), ChordDefinition(key.NUM_ENTER)],
                on_press=on_key_press("="),
            )
        )
        # Make the backspace and escape keys also trigger clear.
        keymap.add_keyboard_action(
            KeyboardActionDefinition(
                chords=[ChordDefinition(key.BACKSPACE), ChordDefinition(key.ESCAPE)],
                on_press=on_key_press("C"),
            )
        )
        return keymap


def create_new_calculator(*_, **__):
    """Create a new calculator and add it to the current scene."""
    # Create a new calculator
    calculator = Calculator()
    calculator.position = 100, 100

    # Add it to the current scene.
    cocos.director.director.scene.add(calculator)

    # Make the new calculator the currently focused window.
    calculator.make_focused()


def main():
    """Run the calculator program."""
    cocos.director.director.init()
    new_calculator_button = Button(
        ButtonDefinition(text="New Calculator", on_press=create_new_calculator)
    )
    new_calculator_button.position = (
        0,
        cocos.director.director.get_window_size()[1]
        - new_calculator_button.rect.height,
    )
    calculator = Calculator()
    calculator.position = 100, 100
    calculator2 = Calculator()
    calculator2.position = 200, 50
    scene = cocos.scene.Scene(new_calculator_button, calculator, calculator2)
    cocos.director.director.run(scene)


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    main()
