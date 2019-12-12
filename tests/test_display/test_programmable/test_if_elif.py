import cocos
import pytest

from concurrent.futures import ThreadPoolExecutor
from time import sleep

from shimmer.engine.programmable.definition import If, Elif, Else
from shimmer.display.programmable.if_elif import (
    IfDisplay,
    ElifDisplay,
    CodeBlockDisplay,
)


def return_true():
    return True


@pytest.fixture
def dummy_elif(dummy_code_block):
    if_ = If(method=return_true, if_block=dummy_code_block)
    if2_ = If(method=return_true, if_block=dummy_code_block)
    else_ = Else(if_block=dummy_code_block)
    instruction = Elif(
        method=return_true, if_block=dummy_code_block, elifs=[if_, if2_], else_=else_
    )
    return instruction


def test_if_display(run_gui, dummy_code_block):
    """If Instruction should be shown with a code block."""
    instruction = If(method=return_true, if_block=dummy_code_block)
    layer = IfDisplay(instruction)
    assert run_gui(test_if_display, layer)


def test_if_display_empty_code_block(run_gui):
    """If Instruction should be shown with empty code block."""
    instruction = If(method=return_true)
    layer = IfDisplay(instruction)
    assert run_gui(test_if_display_empty_code_block, layer)


def test_if_display_active(run_gui, dummy_code_block):
    """Active If instruction should be shown with one active method in code block."""
    instruction = If(
        method=return_true, if_block=dummy_code_block, currently_running=True
    )
    dummy_code_block.instructions[1].currently_running = True
    layer = IfDisplay(instruction)
    assert run_gui(test_if_display_active, layer)


def test_if_else_display(run_gui, dummy_code_block):
    """If / elif / else block should be shown."""
    if_ = If(method=return_true, if_block=dummy_code_block)
    if2_ = If(method=return_true, if_block=dummy_code_block)
    else_ = Else(if_block=dummy_code_block)
    instruction = Elif(
        method=return_true, if_block=dummy_code_block, elifs=[if_, if2_], else_=else_
    )
    layer = ElifDisplay(instruction)
    assert run_gui(test_if_else_display, layer)


def test_elif_display_with_changing_elements(run_gui, dummy_elif):
    """If/elif/else block with changing elements should be shown."""

    def rotate_instructions(code_block_display: CodeBlockDisplay):
        while not cocos.director.director.terminate_app:
            sleep(0.5)
            code_block_display.code_block.instructions = (
                code_block_display.code_block.instructions[1:]
                + code_block_display.code_block.instructions[:1]
            )
            code_block_display.dirty = True

    def add_delete_elif_block(elif_block_display: ElifDisplay):
        elif_block = elif_block_display.instruction.elifs[0]
        while not cocos.director.director.terminate_app:
            sleep(1)
            if elif_block in elif_block_display.instruction.elifs:
                elif_block_display.instruction.elifs.remove(elif_block)
            else:
                elif_block_display.instruction.elifs.insert(0, elif_block)
            elif_block_display.dirty = True

    layer = ElifDisplay(dummy_elif)

    with ThreadPoolExecutor() as executor:
        # Have to run the instruction rotation in a thread because `run_gui` blocks.
        executor.submit(rotate_instructions, layer.if_block_display)
        executor.submit(add_delete_elif_block, layer)
        assert run_gui(test_elif_display_with_changing_elements, layer)
