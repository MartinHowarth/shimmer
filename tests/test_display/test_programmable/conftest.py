import pytest

from shimmer.engine.programmable.definition import CodeBlock, Instruction


@pytest.fixture
def dummy_code_block() -> CodeBlock:
    def one():
        pass

    def two():
        pass

    def three():
        pass

    return CodeBlock(
        instructions=[Instruction(method=method) for method in (one, two, three)]
    )
