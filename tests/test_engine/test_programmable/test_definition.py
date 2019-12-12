import pytest

from textwrap import dedent

from shimmer.engine.programmable.definition import (
    Instruction,
    CodeBlock,
    If,
    Elif,
    Program,
    NOT_YET_RUN,
    Else,
)


def make_dummy_code_block() -> CodeBlock:
    return CodeBlock(instructions=[Instruction(method=return_true) for _ in range(3)])


def make_dummy_if(call_if: bool = True):
    if_block = make_dummy_code_block()
    return If(method=return_true if call_if else return_false, if_block=if_block,)


def make_dummy_elif(call_if: bool = True):
    if_block = make_dummy_code_block()
    else_ = Else(if_block=make_dummy_code_block())
    return Elif(
        method=return_true if call_if else return_false, if_block=if_block, else_=else_,
    )


@pytest.fixture
def dummy_code_block():
    return make_dummy_code_block()


@pytest.fixture
def another_dummy_code_block():
    return make_dummy_code_block()


def assert_code_block_called(code_block: CodeBlock):
    for ins in code_block.instructions:
        assert ins.result is not NOT_YET_RUN


def assert_code_block_not_called(code_block: CodeBlock):
    for ins in code_block.instructions:
        assert ins.result is NOT_YET_RUN


def is_truthy(obj) -> bool:
    return bool(obj)


def return_true() -> bool:
    return True


def return_false() -> bool:
    return False


def test_instruction_no_args():
    ins = Instruction(method=return_true)
    assert ins.result is NOT_YET_RUN

    ins.execute()
    assert ins.result is True


def test_instruction_with_args(subtests):
    with subtests.test("Test true result"):
        ins = Instruction(method=is_truthy, args=(1,))
        ins.execute()
        assert ins.result is True

    with subtests.test("Test false result"):
        ins = Instruction(method=is_truthy, args=(0,))
        ins.execute()
        assert ins.result is False

    with subtests.test("Test multiple arguments"):
        ins = Instruction(method=max, args=(2, 5))
        ins.execute()
        assert ins.result == 5


def test_codeblock_all_instructions_called(dummy_code_block):
    dummy_code_block.run()
    assert_code_block_called(dummy_code_block)


def test_if(subtests, dummy_code_block):
    with subtests.test("Test if test was True, code block was called"):
        if_ = If(method=return_true, if_block=dummy_code_block)
        if_.execute()
        assert_code_block_called(dummy_code_block)

    with subtests.test("Test if test was False, code block was not called"):
        if_ = If(method=return_false, if_block=dummy_code_block)
        if_.execute()
        assert_code_block_called(dummy_code_block)


def test_elif_if_block_called(subtests, dummy_code_block, another_dummy_code_block):
    elif_ = Elif(
        method=return_true,
        if_block=dummy_code_block,
        else_=Else(if_block=another_dummy_code_block),
    )
    elif_.execute()
    assert_code_block_called(dummy_code_block)
    assert_code_block_not_called(another_dummy_code_block)


def test_elif_else_block_called(subtests, dummy_code_block, another_dummy_code_block):
    elif_ = Elif(
        method=return_false,
        if_block=dummy_code_block,
        else_=Else(if_block=another_dummy_code_block),
    )
    elif_.execute()
    assert_code_block_not_called(dummy_code_block)
    assert_code_block_called(another_dummy_code_block)


@pytest.mark.parametrize(
    "block_call_if, expected_called_block_index",
    [
        ((True, True, True, False), 0),  # First If block called
        ((False, True, True, False), 1),  # First elif block called
        ((False, False, True, True), 2),  # Second elif block called
        ((False, False, False, False), 4),  # Else block called
    ],
)
def test_elif(block_call_if, expected_called_block_index):
    if_block = make_dummy_code_block()
    else_block = make_dummy_code_block()

    first_call_if = return_true if block_call_if[0] else return_false
    elifs = [make_dummy_if(call_if) for call_if in block_call_if[1:]]
    elif_ = Elif(
        method=first_call_if,
        if_block=if_block,
        elifs=elifs,
        else_=Else(if_block=else_block),
    )
    elif_.execute()

    all_blocks = [if_block, *(_elif.if_block for _elif in elifs), else_block]

    for index, block in enumerate(all_blocks):
        if index == expected_called_block_index:
            assert_code_block_called(block)
        else:
            assert_code_block_not_called(block)


def test_nested_elif(subtests, dummy_code_block, another_dummy_code_block):
    else_ = Else(
        if_block=CodeBlock(
            instructions=[If(method=return_true, if_block=another_dummy_code_block,)]
        )
    )
    elif_ = Elif(method=return_false, if_block=dummy_code_block, else_=else_,)
    elif_.execute()
    assert_code_block_not_called(dummy_code_block)
    assert_code_block_called(another_dummy_code_block)


def test_program(dummy_code_block):
    program = Program(dummy_code_block)
    program.run()
    assert_code_block_called(dummy_code_block)


def test_instruction_str():
    ins = Instruction(method=max, args=(2, 5))
    assert str(ins) == "max(2, 5)"
    ins.execute()
    assert str(ins) == "max(2, 5) -> 5"


def test_code_block_str(dummy_code_block):
    assert (
        str(dummy_code_block)
        == dedent(
            """
            return_true()
            return_true()
            return_true()
            """
        ).strip()
    )


def test_if_str(dummy_code_block):
    if_ = If(method=return_false, if_block=dummy_code_block)
    assert (
        str(if_)
        == dedent(
            """
            if return_false():
                return_true()
                return_true()
                return_true()
            """
        ).strip()
    )


def test_if_else_str(dummy_code_block):
    else_if = make_dummy_elif(call_if=False)
    assert (
        str(else_if)
        == dedent(
            """
            if return_false():
                return_true()
                return_true()
                return_true()
            else:
                return_true()
                return_true()
                return_true()
            """
        ).strip()
    )


def test_elif_str(dummy_code_block):
    elif_ = Elif(
        method=return_false,
        if_block=dummy_code_block,
        elifs=[make_dummy_if(True), make_dummy_if(False)],
        else_=Else(if_block=dummy_code_block),
    )
    assert (
        str(elif_)
        == dedent(
            """
            if return_false():
                return_true()
                return_true()
                return_true()
            elif return_true():
                return_true()
                return_true()
                return_true()
            elif return_false():
                return_true()
                return_true()
                return_true()
            else:
                return_true()
                return_true()
                return_true()
            """
        ).strip()
    )


def test_nested_if_str(dummy_code_block, another_dummy_code_block):
    else_ = Else(
        if_block=CodeBlock(
            instructions=[If(method=return_true, if_block=another_dummy_code_block,)]
        )
    )
    elif_ = Elif(method=return_false, if_block=dummy_code_block, else_=else_,)
    assert (
        str(elif_)
        == dedent(
            """
            if return_false():
                return_true()
                return_true()
                return_true()
            else:
                if return_true():
                    return_true()
                    return_true()
                    return_true()
            """
        ).strip()
    )
