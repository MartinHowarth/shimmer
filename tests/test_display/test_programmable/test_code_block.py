"""Test the graphical display of a CodeBlock."""

import time
from concurrent.futures import ThreadPoolExecutor

import cocos
from shimmer.programmable.code_block import (
    CodeBlockDisplay,
    CodeBlock,
    CodeBlockDisplayDefinition,
)
from shimmer.programmable.logic.definition import Instruction


def test_code_block_display(run_gui, dummy_code_block):
    """Code block should be shown."""
    layer = CodeBlockDisplay(dummy_code_block, CodeBlockDisplayDefinition())
    assert run_gui(test_code_block_display, layer)


def test_code_block_display_on_loop(run_gui):
    """Code block with instructions being run sequentially should be shown."""

    def wait_1():
        """An dummy instruction method that takes a while to run."""
        time.sleep(0.5)

    code_block = CodeBlock(instructions=[Instruction(method=wait_1) for _ in range(3)])

    def loop_code_block(_code_block: CodeBlock) -> None:
        """Run the instruction repeatedly with a sleep in between."""
        while not cocos.director.director.terminate_app:
            _code_block.run()
            time.sleep(0.5)

    layer = CodeBlockDisplay(code_block, CodeBlockDisplayDefinition())

    with ThreadPoolExecutor() as executor:
        # Start the loop in a thread because `run_gui` blocks.
        executor.submit(loop_code_block, code_block)
        assert run_gui(test_code_block_display_on_loop, layer)
