import logging

from typing import cast, Optional, List

from shimmer.display.programmable.instruction import InstructionDisplay
from shimmer.display.programmable.code_block import CodeBlockDisplay
from shimmer.engine.programmable.definition import (
    Elif,
    If,
    Else,
)

log = logging.getLogger(__name__)


class IfDisplay(InstructionDisplay):
    indentation = 20

    def __init__(self, instruction: If):
        super(IfDisplay, self).__init__(instruction)
        self.instruction = cast(If, self.instruction)
        self.if_block_display = CodeBlockDisplay(self.instruction.if_block)
        self.if_block_display.position = self.indentation, 0
        self.add(self.if_block_display)

    @property
    def total_height(self):
        return self.if_block_display.height + self.height


class ElifBlockDisplay(IfDisplay):
    text_format = "el{}"


class ElseBlockDisplay(IfDisplay):
    instruction: Else


class ElifDisplay(IfDisplay):
    instruction: Elif

    def __init__(self, instruction: Elif):
        super(ElifDisplay, self).__init__(instruction)
        self.elif_displays = []  # type: List[ElifBlockDisplay]
        self.else_display = None  # type: Optional[ElseBlockDisplay]
        self.add_else_display()
        self.refresh_elifs()

    def _if_elif_height(self):
        total = super(ElifDisplay, self).total_height
        total += sum([elif_display.total_height for elif_display in self.elif_displays])
        return total

    @property
    def total_height(self):
        total = self._if_elif_height()
        if self.else_display is not None:
            total += self.else_display.total_height
        return total

    def refresh_elifs(self):
        for z, child in self.children:
            if isinstance(child, ElifBlockDisplay):
                self.remove(child)
        self.elif_displays = []
        self.add_elif_displays()

    def add_elif_displays(self):
        for _elif in self.instruction.elifs:
            elif_display = ElifBlockDisplay(_elif)
            elif_display.position = 0, -self._if_elif_height()
            self.add(elif_display)
            self.elif_displays.append(elif_display)

        if self.else_display is not None:
            # Update else display to be at the bottom
            self.else_display.position = (
                0,
                -self._if_elif_height(),
            )

    def add_else_display(self):
        else_display = ElseBlockDisplay(self.instruction.else_)
        else_display.position = 0, -self.total_height
        self.add(else_display)
        self.else_display = else_display

    def _update(self, dt: float):
        super(ElifDisplay, self)._update(dt)
        self.refresh_elifs()
