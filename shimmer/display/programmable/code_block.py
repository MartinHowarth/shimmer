"""Graphical display of a set of programmable code instructions."""

import logging

from shimmer.display.data_structures import Color
from shimmer.display.primitives import UpdatingNode, create_rect
from shimmer.display.programmable.instruction import InstructionDisplay
from shimmer.engine.programmable.definition import CodeBlock

log = logging.getLogger(__name__)


class CodeBlockDisplay(UpdatingNode):
    """Graphical display of a set of programmable code instructions."""

    def __init__(self, code_block: CodeBlock):
        """
        Create a new CodeBlockDisplay.

        :param code_block: The code block to display.
        """
        super(CodeBlockDisplay, self).__init__()
        self.code_block = code_block
        self.refresh_children()

    @property
    def height(self):
        """Total pixel height of this code block display."""
        return sum(
            [child[1].height for child in self.children if hasattr(child[1], "height")]
        )

    def refresh_children(self):
        """Recreate the entire display of this code block."""
        self.children.clear()

        if len(self.code_block.instructions) == 0:
            null_rect = create_rect(100, 15, Color(150, 0, 0))
            null_rect.position = 0, -null_rect.height
            self.add(null_rect)

        for index, instruction in enumerate(self.code_block.instructions):
            ins_display = InstructionDisplay(instruction)
            ins_display.position = 0, -(index + 1) * ins_display.height
            self.add(ins_display)

    def _update(self, dt: float):
        """Called when this Node is dirty to update the display."""
        self.refresh_children()
