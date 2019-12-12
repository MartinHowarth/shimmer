from shimmer.display.programmable.instruction import InstructionDisplay, Instruction


def test_instruction_display(run_gui):
    """Instruction should be shown."""
    instruction = Instruction(method=max, args=(3, 5))
    layer = InstructionDisplay(instruction)
    assert run_gui(test_instruction_display, layer)


def test_instruction_display_active(run_gui):
    """Instruction should be shown in an activated state."""
    instruction = Instruction(method=max, args=(3, 5), currently_running=True)
    layer = InstructionDisplay(instruction)
    assert run_gui(test_instruction_display_active, layer)
