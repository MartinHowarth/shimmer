"""Visual display of a code block Instruction."""

import logging
from dataclasses import dataclass, replace
from typing import Optional

import cocos
from shimmer.display.components.box import BoxDefinition
from shimmer.display.components.draggable_anchor import DraggableAnchor
from shimmer.display.data_structures import Color, ActiveGreen
from shimmer.display.primitives import create_color_rect
from shimmer.display.widgets.button import ButtonDefinition, Button
from shimmer.engine.programmable.definition import Instruction

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class InstructionDisplayDefinition(ButtonDefinition):
    """
    Definition of the visual display of an Instruction.

    If text is None, then it will be set to the formatted `method_str` of the instruction.
    """

    # Color to display over the Instruction button while the instruction is being executed.
    while_executing_mask: Optional[Color] = replace(ActiveGreen, a=100)
    # String format to use. Will be formatted with `instruction.method_str()`.
    text_format: str = "{}"
    # Whether the instruction should be draggable.
    draggable: bool = False
    # The width of the draggable anchor for this instruction.
    draggable_width: int = 20


class InstructionDisplay(Button):
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
        button_text = self.get_button_text(instruction, definition)
        definition = replace(definition, text=button_text)
        self.instruction = instruction

        self.instruction.on_execute_start = self.show_mask
        self.instruction.on_execute_complete = self.hide_mask

        self.drag_anchor: Optional[DraggableAnchor] = None
        self.executing_mask: Optional[cocos.layer.ColorLayer] = None

        super(InstructionDisplay, self).__init__(definition)
        self.definition: InstructionDisplayDefinition = definition
        self.update_draggable_anchor()
        self.update_mask()

    def on_size_change(self):
        """Update children as needed if the size of this Box changes."""
        super(InstructionDisplay, self).on_size_change()
        self.update_mask()

    @staticmethod
    def get_button_text(
        instruction: Instruction, definition: InstructionDisplayDefinition
    ) -> Optional[str]:
        """
        Get the text of the button should display.

        By default it will be `instruction.method_str()` applied to the defined text_format.
        """
        if definition.text is None:
            return definition.text_format.format(instruction.method_str())
        else:
            return None

    def update_draggable_anchor(self):
        """Re-create the draggable anchor."""
        if self.drag_anchor is not None:
            self.remove(self.drag_anchor)

        if self.definition.draggable is False:
            self.drag_anchor = None
            return

        self.drag_anchor = DraggableAnchor(
            BoxDefinition(
                width=self.definition.draggable_width, height=self.rect.height
            )
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
        self.executing_mask = create_color_rect(
            width=self.rect.width,
            height=self.rect.height,
            color=replace(self.definition.while_executing_mask, a=0),
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
