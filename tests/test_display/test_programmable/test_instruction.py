"""Tests for the graphical display of a code block instruction."""

import cocos
import pytest
import time

from concurrent.futures import ThreadPoolExecutor

from shimmer.display.programmable.instruction import (
    InstructionDisplay,
    InstructionDisplayDefinition,
)
from shimmer.engine.programmable.definition import Instruction


@pytest.fixture
def dummy_instruction():
    """Common definition of a instruction for use in the tests."""
    return Instruction(method=max, args=(3, 5))


def test_instruction_display_default(run_gui, dummy_instruction):
    """Instruction should be shown."""
    defn = InstructionDisplayDefinition()
    layer = InstructionDisplay(dummy_instruction, defn)
    assert run_gui(test_instruction_display_default, layer)


def test_instruction_display_active(run_gui, dummy_instruction):
    """Instruction should be shown in an activated state."""
    defn = InstructionDisplayDefinition()
    layer = InstructionDisplay(dummy_instruction, defn)
    layer.show_mask()
    assert run_gui(test_instruction_display_active, layer)


def test_instruction_display_draggable(run_gui, dummy_instruction):
    """Instruction should be draggable from the left hand side.."""
    defn = InstructionDisplayDefinition(draggable=True)
    layer = InstructionDisplay(dummy_instruction, defn)
    assert run_gui(test_instruction_display_draggable, layer)


def test_instruction_display_on_loop(run_gui):
    """Instruction should be shown alternatively active then inactive."""

    def wait_1():
        """An dummy instruction method that takes a while to run."""
        time.sleep(0.5)

    instruction = Instruction(method=wait_1)

    def loop_instruction(_instruction: Instruction):
        """Run the instruction repeatedly with a sleep in between."""
        while not cocos.director.director.terminate_app:
            _instruction.execute()
            time.sleep(0.5)

    layer = InstructionDisplay(instruction, InstructionDisplayDefinition())

    with ThreadPoolExecutor() as executor:
        # Start the loop in a thread because `run_gui` blocks.
        executor.submit(loop_instruction, instruction)
        assert run_gui(test_instruction_display_on_loop, layer)
