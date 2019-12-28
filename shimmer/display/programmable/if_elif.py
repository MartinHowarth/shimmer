"""Visual display of a code block If/Else/Elif statement."""

import logging

from dataclasses import dataclass, field
from typing import cast, Optional, List

from shimmer.display.components.box import Box, BoxDefinition
from shimmer.display.components.box_layout import BoxColumn
from shimmer.display.programmable.instruction import (
    InstructionDisplay,
    InstructionDisplayDefinition,
)
from shimmer.display.programmable.code_block import (
    CodeBlockDisplay,
    CodeBlockDisplayDefinition,
)
from shimmer.engine.programmable.definition import (
    InstructionWithCodeBlock,
    IfElifElse,
)

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class InstructionWithBlockDisplayDefinition(BoxDefinition):
    """Definition of how to display an instruction with an associated CodeBlock."""

    # Definition of the main If statement display
    instruction_definition: InstructionDisplayDefinition = field(
        default_factory=InstructionDisplayDefinition
    )
    # Definition of the code block display within the If statement.
    code_block_definition: CodeBlockDisplayDefinition = field(
        default_factory=CodeBlockDisplayDefinition
    )
    # How far the code block is indented by compared to the If instruction.
    code_block_indentation: int = 20


class InstructionWithBlockDisplay(Box):
    """
    Graphical display of an instruction with a nested code block.

    Consists of:
      - an InstructionDisplay
      - a CodeBlockDisplay below that, indented by a configurable amount.
    """

    def __init__(
        self,
        instruction: InstructionWithCodeBlock,
        definition: InstructionWithBlockDisplayDefinition,
    ):
        """
        Create an IfElifElseDisplay.

        :param instruction: The InstructionWithCodeBlock instruction to display.
        :param definition: The definition of the display style to use for the code block.
        """
        super(InstructionWithBlockDisplay, self).__init__()
        self.instruction: InstructionWithCodeBlock = instruction
        self.definition: InstructionWithBlockDisplayDefinition = definition
        self.instruction_display: Optional[InstructionDisplay] = None
        self.code_block_display: Optional[CodeBlockDisplay] = None
        self.update_boxes()

    def update_boxes(self):
        """Recreate the child boxes of this display."""
        if self.instruction_display is not None:
            self.remove(self.instruction_display)
        if self.code_block_display is not None:
            self.remove(self.code_block_display)
        self.code_block_display = CodeBlockDisplay(
            self.instruction.code_block, self.definition.code_block_definition
        )
        self.code_block_display.position = self.definition.code_block_indentation, 0
        self.instruction_display = InstructionDisplay(
            self.instruction, self.definition.instruction_definition
        )
        self.instruction_display.position = 0, self.code_block_display.rect.height
        self.set_size(
            max(
                self.code_block_display.rect.width
                + self.definition.code_block_indentation,
                self.instruction_display.rect.width,
            ),
            self.code_block_display.rect.height + self.instruction_display.rect.height,
        )
        self.add(self.instruction_display)
        self.add(self.code_block_display)


class IfElifElseDisplay(BoxColumn):
    """
    A vertical arrangement of InstructionWithBlockDisplays to display an If/Elif/Else block.

    Produces output similar to:
    if method():
        if_method1()
    elif method2():
        elif_method()
    else:
        pass
    """

    def __init__(
        self,
        instruction: IfElifElse,
        definition: InstructionWithBlockDisplayDefinition,
    ):
        """
        Create an IfElifElseDisplay.

        :param instruction: The IfElifElse instruction to display.
        :param definition: The definition of the display style to use for each code block.
        """
        super(IfElifElseDisplay, self).__init__([], 0)
        self.instruction: IfElifElse = instruction
        self.definition: InstructionWithBlockDisplayDefinition = definition

        self._boxes = cast(List[InstructionWithBlockDisplay], self._boxes)

        self.update_boxes()

    def update_boxes(self):
        """Recreate the child boxes of this display."""
        for display in self._boxes:
            self.remove(display)

        for _elif in self.instruction.elifs:
            elif_display = InstructionWithBlockDisplay(_elif, self.definition)
            # Insert at start of list so we get a top-to-bottom list, which matches how the code
            # will be executed.
            self.add(elif_display, position=0)

        if self.instruction.else_ is not None:
            else_display = InstructionWithBlockDisplay(
                self.instruction.else_, self.definition
            )
            # Insert at start of list so we get Else at the bottom.
            self.add(else_display, position=0)

        # Add instruction last so it appears at the top.
        instruction_display = InstructionWithBlockDisplay(
            self.instruction, self.definition
        )
        self.add(instruction_display)
