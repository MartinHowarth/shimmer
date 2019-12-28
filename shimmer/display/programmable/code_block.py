"""Graphical display of a set of programmable code instructions."""

import logging

from dataclasses import dataclass, field
from typing import List, cast

from shimmer.display.components.box import BoxDefinition
from shimmer.display.components.box_layout import BoxColumn
from shimmer.display.programmable.instruction import (
    InstructionDisplay,
    InstructionDisplayDefinition,
)
from shimmer.engine.programmable.definition import CodeBlock

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class CodeBlockDisplayDefinition(BoxDefinition):
    """Definition of how to display a CodeBlock."""

    instruction_definition: InstructionDisplayDefinition = field(
        default_factory=InstructionDisplayDefinition
    )
    # Spacing between the vertically arranged instructions.
    spacing: int = 0


class CodeBlockDisplay(BoxColumn):
    """Graphical display of a set of programmable code instructions."""

    def __init__(
        self, code_block: CodeBlock, code_block_definition: CodeBlockDisplayDefinition,
    ):
        """
        Create a new CodeBlockDisplay.

        :param code_block: The code block to display.
        """
        super(CodeBlockDisplay, self).__init__([], code_block_definition.spacing)
        self.code_block: CodeBlock = code_block
        self.definition: CodeBlockDisplayDefinition = code_block_definition

        self._boxes = cast(List[InstructionDisplay], self._boxes)
        self.update_instructions()

    def update_instructions(self):
        """Re-create all instruction displays."""
        # We could enhance this later to only re-create those that have
        # changed, but keep it simple for starters.
        for instruction_display in self._boxes:
            self.remove(instruction_display)

        for instruction in self.code_block.instructions:
            new_display = InstructionDisplay(
                instruction, self.definition.instruction_definition
            )
            # Insert at start of list so we get a top-to-bottom list, which matches how the code
            # will be executed.
            self.add(new_display, position=0)
