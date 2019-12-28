"""Example of a simple calculator written using shimmer."""

import cocos

from typing import Optional, List

from shimmer.display.widgets.button import ButtonDefinition, Button
from shimmer.display.widgets.window import WindowDefinition, Window
from shimmer.display.widgets.text_box import TextBoxDefinition, TextBox
from shimmer.display.data_structures import (
    VerticalAlignment,
    HorizontalAlignment,
)
from shimmer.display.components.box_layout import create_box_layout, BoxLayoutDefinition


class Calculator(Window):
    """A simple calculator."""

    symbol_layout = [
        ["7", "8", "9", "+"],
        ["4", "5", "6", "-"],
        ["1", "2", "3", "/"],
        ["C", "0", "=", "*"],
    ]
    layout_definition = BoxLayoutDefinition(boxes_per_row=4, boxes_per_column=4)
    margin = 30

    def __init__(self):
        """Create a Calculator."""
        self.calculation: str = ""
        self.result: Optional[str] = None

        # Create all the calculator buttons.
        self.buttons = self.create_buttons()

        # Arrange them into a grid layout.
        self.button_layout = create_box_layout(self.layout_definition, self.buttons)
        # Get the size of that layout
        layout_rect = self.button_layout.bounding_rect_of_children()
        # Create the calculator display
        self.text_box = TextBox(
            TextBoxDefinition(width=layout_rect.width - 2 * self.margin, height=30)
        )
        # Define the window to be large enough to contain the buttons.
        definition = WindowDefinition(
            title="Calculator",
            title_bar_height=None,
            width=layout_rect.width + 2 * self.margin,
            height=layout_rect.height + self.text_box.rect.height + 2 * self.margin,
        )
        super(Calculator, self).__init__(definition)

        # Add the display and the buttons to the Window body with sensible alignment.
        self.add_child_to_body(
            self.text_box,
            align_x=HorizontalAlignment.left,
            margin_x=self.margin,
            align_y=VerticalAlignment.top,
            margin_y=self.margin,
        )
        self.add_child_to_body(self.button_layout)

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
            ButtonDefinition(text=symbol, on_press=callback, width=50, height=50)
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


if __name__ == "__main__":
    cocos.director.director.init()
    calculator = Calculator()
    calculator.position = 100, 100
    scene = cocos.scene.Scene(calculator)
    cocos.director.director.run(scene)
