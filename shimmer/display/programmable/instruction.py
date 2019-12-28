"""Visual display of a code block Instruction."""

import cocos
import logging

from dataclasses import dataclass, field, replace
from typing import Optional


from shimmer.display.components.box import Box, BoxDefinition
from shimmer.display.data_structures import Color, ActiveGreen
from shimmer.display.components.draggable_anchor import DraggableAnchor
from shimmer.display.widgets.button import ButtonDefinition, Button

from shimmer.engine.programmable.definition import Instruction

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class InstructionDisplayDefinition(BoxDefinition):
    """Definition of the visual display of an Instruction."""

    # The main element of this instruction is a button. If the text is None, then it will be
    # set to the formatted `method_str` of the instruction.
    button_definition: ButtonDefinition = field(default_factory=ButtonDefinition)
    # Color to display over the Instruction button while the instruction is being executed.
    while_executing_mask: Optional[Color] = replace(ActiveGreen, a=100)
    # String format to use. Will be formatted with `instruction.method_str()`.
    text_format: str = "{}"
    # Whether the instruction should be draggable.
    draggable: bool = False
    # The width of the draggable anchor for this instruction.
    draggable_width: int = 20


class InstructionDisplay(Box):
    """
    Display for a code block Instruction.

    Comprised of 3 Boxes:
      - A Button - e.g. for allowing the user to edit the instruction.
      - A drag anchor aligned on the left of the button.
      - A color mask that overlays the button while the instruction is being executed.
    """

    def __init__(
        self, instruction: Instruction, definition: InstructionDisplayDefinition
    ):
        """
        Create an InstructionDisplay.

        :param instruction: The Instruction to display.
        :param definition: Definition of the display of the Instruction.
        """
        super(InstructionDisplay, self).__init__(definition)
        self.instruction = instruction
        self.definition: InstructionDisplayDefinition = definition

        self.instruction.on_execute_start = self.show_mask
        self.instruction.on_execute_complete = self.hide_mask

        self.button: Optional[Button] = None
        self.drag_anchor: Optional[DraggableAnchor] = None
        self.executing_mask: Optional[cocos.layer.ColorLayer] = None
        self.update_button()
        self.update_draggable_anchor()
        self.update_mask()

    def get_button_text(self) -> Optional[str]:
        """
        Get the text of the button should display.

        By default it will be `instruction.method_str()` applied to the defined text_format.
        """
        if self.definition.button_definition.text is None:
            return self.definition.text_format.format(self.instruction.method_str())
        else:
            return None

    def update_button(self):
        """Re-create the button Box."""
        if self.button is not None:
            self.remove(self.button)

        # Make a duplicate of the definition for the actual button with the correct text.
        text = self.get_button_text()
        button_definition = replace(self.definition.button_definition, text=text)

        self.button = Button(button_definition)
        if (
            self.definition.button_definition.height is None
            or self.definition.button_definition.width is None
        ):
            # And update this rect to match the buttons dynamic size
            self.rect = self.button.rect
            self.update_mask()
        self.add(self.button, z=0)

    def update_draggable_anchor(self):
        """Re-create the draggable anchor."""
        if self.drag_anchor is not None:
            self.remove(self.drag_anchor)

        if self.definition.draggable is False:
            self.drag_anchor = None
            return

        self.drag_anchor = DraggableAnchor(
            cocos.rect.Rect(0, 0, self.definition.draggable_width, self.rect.height)
        )
        self.add(self.drag_anchor, z=1)

    def update_mask(self):
        """Re-create the color mask, starting off invisible."""
        if self.executing_mask is not None:
            self.remove(self.executing_mask)

        if self.definition.while_executing_mask is None:
            self.executing_mask = None
            return

        # Create the mask invisible (with 0 opacity), it should be made visible using the
        # instruction callbacks.
        self.executing_mask = cocos.layer.ColorLayer(
            *self.definition.while_executing_mask.as_tuple(),
            0,
            width=self.rect.width,
            height=self.rect.height
        )
        self.add(self.executing_mask, z=1)

    def show_mask(self):
        """Make the color mask visible."""
        if (
            self.executing_mask is not None
            and self.definition.while_executing_mask is not None
        ):
            self.executing_mask.opacity = self.definition.while_executing_mask.a

    def hide_mask(self):
        """Make the color mask invisible."""
        if self.executing_mask is not None:
            self.executing_mask.opacity = 0
