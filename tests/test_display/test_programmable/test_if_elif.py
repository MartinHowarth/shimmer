"""Tests for the graphical display of If/Elif/Else code blocks."""

import cocos
import time

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

from shimmer.engine.programmable.definition import If, IfElifElse
from shimmer.display.programmable.if_elif import (
    InstructionWithBlockDisplay,
    IfElifElseDisplay,
    InstructionWithBlockDisplayDefinition,
)

from .conftest import return_false, return_true


def test_if_display(run_gui, dummy_code_block):
    """If Instruction should be shown with a code block."""
    instruction = If(method=return_true, code_block=dummy_code_block)
    layer = InstructionWithBlockDisplay(
        instruction, InstructionWithBlockDisplayDefinition()
    )
    assert run_gui(test_if_display, layer)


def test_if_display_empty_code_block(run_gui):
    """If Instruction should be shown with empty code block."""
    instruction = If(method=return_true)
    layer = InstructionWithBlockDisplay(
        instruction, InstructionWithBlockDisplayDefinition()
    )
    assert run_gui(test_if_display_empty_code_block, layer)


def test_if_else_display(run_gui, dummy_elif):
    """If / else block should be shown with no elifs."""
    if_else_defn = replace(dummy_elif, elifs=[])
    layer = IfElifElseDisplay(if_else_defn, InstructionWithBlockDisplayDefinition())
    assert run_gui(test_if_else_display, layer)


def test_if_elif_else_display(run_gui, dummy_elif):
    """If / elif / else block should be shown."""
    layer = IfElifElseDisplay(dummy_elif, InstructionWithBlockDisplayDefinition())
    assert run_gui(test_if_elif_else_display, layer)


def test_if_elif_else_display_on_loop(run_gui, dummy_elif):
    """Code block with the first Elif block instruction being run sequentially should be shown."""
    # Make it so that the first Elif statement gets run
    dummy_elif.method = return_false

    def loop_code_block(instruction: IfElifElse) -> None:
        """Run the instruction repeatedly with a sleep in between."""
        while not cocos.director.director.terminate_app:
            instruction.execute()
            time.sleep(0.5)

    layer = IfElifElseDisplay(dummy_elif, InstructionWithBlockDisplayDefinition())
    with ThreadPoolExecutor() as executor:
        # Start the loop in a thread because `run_gui` blocks.
        executor.submit(loop_code_block, dummy_elif)
        assert run_gui(test_if_elif_else_display_on_loop, layer)
