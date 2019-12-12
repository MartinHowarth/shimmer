import pytest

from shimmer.engine.programmable.base import Programmable


def return_true() -> bool:
    return True


def return_false() -> bool:
    return False


def return_str() -> str:
    return ""


@pytest.fixture
def dummy_programmable():
    return Programmable(methods={return_true, return_false, return_str})


def test_bool_methods(dummy_programmable: Programmable):
    bool_methods = list(dummy_programmable.bool_methods)
    assert len(bool_methods) == 2
    assert return_false in bool_methods
    assert return_true in bool_methods
