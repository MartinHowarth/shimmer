"""Pytest fixtures for programmable GUI components."""

import pytest
import time

from shimmer.engine.programmable.definition import (
    CodeBlock,
    Instruction,
    IfElifElse,
    Else,
    Elif,
)


def return_true():
    """Return True."""
    return True


def return_false():
    """Return False."""
    return False


def make_dummy_code_block() -> CodeBlock:
    """Code block definition for use in many tests."""

    def one():
        time.sleep(0.1)

    def two():
        time.sleep(0.2)

    def three():
        time.sleep(0.3)

    return CodeBlock(
        instructions=[Instruction(method=method) for method in (one, two, three)]
    )


def make_dummy_elif():
    """If/Elif/Elif/Else block definition for use in many tests."""
    elif_ = Elif(method=return_true, code_block=make_dummy_code_block())
    elif2_ = Elif(method=return_true, code_block=make_dummy_code_block())
    else_ = Else(code_block=make_dummy_code_block())
    instruction = IfElifElse(
        method=return_true,
        code_block=make_dummy_code_block(),
        elifs=[elif_, elif2_],
        else_=else_,
    )
    return instruction


@pytest.fixture
def dummy_code_block() -> CodeBlock:
    """Fixture of a code block definition for use in many tests."""
    return make_dummy_code_block()


@pytest.fixture
def dummy_elif(dummy_code_block):
    """Fixture of If/Elif/Elif/Else block definition for use in many tests."""
    return make_dummy_elif()
