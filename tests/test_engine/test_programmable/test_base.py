"""Tests for common programmable code block elements."""

import pytest

from shimmer.engine.programmable.base import Programmable


def return_true() -> bool:
    """Return True."""
    return True


def return_false() -> bool:
    """Return False."""
    return False


def return_str() -> str:
    """Return empty string."""
    return ""


@pytest.fixture
def dummy_programmable():
    """Common programmable object for use in these tests."""
    return Programmable(methods={return_true, return_false, return_str})


def test_bool_methods(dummy_programmable: Programmable) -> None:
    """Test that Boolean methods are detected correctly."""
    bool_methods = list(dummy_programmable.bool_methods)
    assert len(bool_methods) == 2
    assert return_false in bool_methods
    assert return_true in bool_methods
