"""Definition of code blocks."""

from dataclasses import dataclass, field
from textwrap import indent
from typing import List, Callable, Any, Optional, Tuple


NOT_YET_RUN = object()


def return_true() -> bool:
    """Return True."""
    return True


@dataclass
class Instruction:
    """A single code instruction."""

    method: Callable
    args: Tuple = field(default_factory=tuple)
    result: Optional[Any] = NOT_YET_RUN

    on_execute_start: Optional[Callable] = None
    on_execute_complete: Optional[Callable] = None

    def execute(self):
        """Run the instruction."""
        if self.on_execute_start is not None:
            self.on_execute_start()
        self.result = self.method(*self.args)
        if self.on_execute_complete is not None:
            self.on_execute_complete()

    def method_str(self) -> str:
        """Return the string representation of the instruction."""
        result_str = f" -> {self.result}" if self.result is not NOT_YET_RUN else ""
        arg_str = ", ".join((str(arg) for arg in self.args))
        return f"{self.method.__name__}({arg_str}){result_str}"

    def __str__(self) -> str:
        """Return the string representation of the instruction."""
        return self.method_str()


@dataclass
class CodeBlock:
    """A collection of instructions."""

    instructions: List[Instruction] = field(default_factory=list)

    def run(self) -> None:
        """Run all the instructions sequentially."""
        for instruction in self.instructions:
            instruction.execute()

    def __str__(self) -> str:
        """Return the string representation of all instructions."""
        return "\n".join((str(ins) for ins in self.instructions))


@dataclass
class InstructionWithCodeBlock(Instruction):
    """
    Definition of an instruction with a code block.

    Generally won't be used directly, but is a common base class for If/While instructions.
    """

    code_block: CodeBlock = field(default_factory=CodeBlock)


@dataclass
class If(InstructionWithCodeBlock):
    """
    Definition of an If block.

    Built of:
      - A single boolean instruction.
      - A code block to execute if that instruction returns True.
    """

    def execute(self):
        """Run the If statement. Only run the code_block if the statement returns True."""
        super(If, self).execute()
        if self.result:
            if self.on_execute_start is not None:
                self.on_execute_start()
            self.code_block.run()
            if self.on_execute_complete is not None:
                self.on_execute_complete()

    def method_str(self) -> str:
        """Return the string representation of the If statement without the code block."""
        return "if {}:".format(super(If, self).method_str())

    def __str__(self) -> str:
        """Return the string representation of the If statement and code block."""
        instruction_str = super(If, self).__str__()
        code_block_str = indent(str(self.code_block), "    ")
        return f"{instruction_str}\n{code_block_str}"


@dataclass
class Else(If):
    """An Else block. Only for use with an Elif block."""

    # We're treating an Else block like an If block that always return True.
    method: Callable = return_true

    def method_str(self) -> str:
        """Return the string representation of the header of the else block."""
        return "else:"


@dataclass
class Elif(If):
    """
    An Elif code block.

    Not intended to be used directly, should be used as part of an IfElifElse.
    """

    def method_str(self) -> str:
        """Return the string representation of the Elif statement without the code block."""
        if_str = super(Elif, self).method_str()
        return "el{}".format(if_str)


@dataclass
class IfElifElse(If):
    """
    An If/Elif/Else block.

    Optionally has 0 or many Elif blocks.
    Optionally has 0 or 1 Else block.
    """

    elifs: List[Elif] = field(default_factory=list)

    # Default to a blank Else block which performs no action.
    else_: Else = field(default_factory=Else)

    def execute(self):
        """Run the Elif block."""
        super(IfElifElse, self).execute()
        if not self.result:  # Result of super If statement
            for if_ in self.elifs:
                if_.execute()
                if if_.result:
                    break
            else:  # If no if_ returned True, then call the else.
                self.else_.execute()

    def __str__(self) -> str:
        """Return the string representation of the Elif block."""
        result = super(IfElifElse, self).__str__() + "\n"
        for _elif in self.elifs:
            result += str(_elif) + "\n"
        result += str(self.else_)
        return result


@dataclass
class Program:
    """
    Definition of a runnable program.

    Constructed of a code block and attributes naming this program.
    """

    name: str
    code_block: CodeBlock

    def run(self) -> None:
        """Run the programs code block."""
        self.code_block.run()
