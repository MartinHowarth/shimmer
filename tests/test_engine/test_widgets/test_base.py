"""Tests for common widget elements."""

import pytest

from shimmer.engine.widgets.base import FloatRange


@pytest.fixture
def dummy_float_range() -> FloatRange:
    """Common FloatRange for use in widget tests."""
    return FloatRange(20, 100)


def test_float_range_contains(dummy_float_range: FloatRange) -> None:
    """Test the contains method of the FloatRange class."""
    # Check `__contains__`
    assert 12 not in dummy_float_range
    assert 50 in dummy_float_range

    # Check upper and lower bounds
    assert dummy_float_range.contains(20)
    assert dummy_float_range.contains(100)


def test_float_range_len(dummy_float_range: FloatRange) -> None:
    """Test the len method of the FloatRange class."""
    assert dummy_float_range.len() == 80
