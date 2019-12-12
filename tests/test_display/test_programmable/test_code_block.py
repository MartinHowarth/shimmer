import cocos

from concurrent.futures import ThreadPoolExecutor
from time import sleep


from shimmer.display.programmable.code_block import CodeBlockDisplay, CodeBlock


def test_code_block_empty_display(run_gui):
    """Empty code block should be shown."""
    code_block = CodeBlock()
    layer = CodeBlockDisplay(code_block)
    assert run_gui(test_code_block_empty_display, layer)


def test_code_block_display(run_gui, dummy_code_block):
    """Code block should be shown."""
    layer = CodeBlockDisplay(dummy_code_block)
    assert run_gui(test_code_block_display, layer)


def test_code_block_display_active(run_gui, dummy_code_block):
    """Code block with one activated instruction should be shown."""
    dummy_code_block.instructions[1].currently_running = True
    layer = CodeBlockDisplay(dummy_code_block)
    assert run_gui(test_code_block_display_active, layer)


def test_code_block_display_changing_instructions(run_gui, dummy_code_block):
    """Code block with instructions changing position should be shown."""

    def rotate_instructions(code_block_display: CodeBlockDisplay):
        while not cocos.director.director.terminate_app:
            sleep(0.5)
            code_block_display.code_block.instructions = (
                code_block_display.code_block.instructions[1:]
                + code_block_display.code_block.instructions[:1]
            )
            code_block_display.dirty = True

    layer = CodeBlockDisplay(dummy_code_block)

    with ThreadPoolExecutor() as executor:
        # Have to run the instruction rotation in a thread because `run_gui` blocks.
        executor.submit(rotate_instructions, layer)
        assert run_gui(test_code_block_display_changing_instructions, layer)
