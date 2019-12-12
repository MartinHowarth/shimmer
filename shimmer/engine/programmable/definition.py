from dataclasses import dataclass, field
from textwrap import indent
from typing import List, Callable, Any, Optional, Tuple


NOT_YET_RUN = object()


def return_true():
    return True


@dataclass
class Instruction:
    method: Callable
    args: Tuple = field(default_factory=tuple)
    result: Optional[Any] = NOT_YET_RUN
    currently_running: bool = False

    def execute(self):
        self.currently_running = True
        self.result = self.method(*self.args)
        self.currently_running = False

    def method_str(self) -> str:
        result_str = f" -> {self.result}" if self.result is not NOT_YET_RUN else ""
        arg_str = ", ".join((str(arg) for arg in self.args))
        return f"{self.method.__name__}({arg_str}){result_str}"

    def __str__(self) -> str:
        return self.method_str()


@dataclass
class CodeBlock:
    instructions: List[Instruction] = field(default_factory=list)

    def run(self) -> None:
        for instruction in self.instructions:
            instruction.execute()

    def __str__(self) -> str:
        return "\n".join((str(ins) for ins in self.instructions))


@dataclass
class If(Instruction):
    if_block: CodeBlock = field(default_factory=CodeBlock)

    def execute(self):
        super(If, self).execute()
        if self.result:
            self.currently_running = True
            self.if_block.run()
            self.currently_running = False

    def method_str(self) -> str:
        return "if {}:".format(super(If, self).method_str())

    def __str__(self) -> str:
        instruction_str = super(If, self).__str__()
        code_block_str = indent(str(self.if_block), "    ")
        return f"{instruction_str}\n{code_block_str}"


@dataclass
class Else(If):
    method: Callable = return_true

    def method_str(self) -> str:
        return "else:"


@dataclass
class Elif(If):
    elifs: List[If] = field(default_factory=list)
    else_: Else = field(default_factory=Else)

    def execute(self):
        super(Elif, self).execute()
        if not self.result:  # Result of super If statement
            for if_ in self.elifs:
                if_.execute()
                if if_.result:
                    break
            else:  # If no if_ returned True, then call the else.
                self.else_.execute()

    def __str__(self) -> str:
        result = super(Elif, self).__str__() + "\n"
        for _elif in self.elifs:
            result += f"el{str(_elif)}\n"
        result += str(self.else_)
        return result


@dataclass
class Program:
    code_block: CodeBlock

    def run(self) -> None:
        self.code_block.run()
