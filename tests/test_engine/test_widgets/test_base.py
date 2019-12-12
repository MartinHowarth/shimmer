import pytest

from shimmer.engine.widgets.base import FloatRange


@pytest.fixture
def dummy_float_range():
    return FloatRange(20, 100)


def test_float_range_contains(dummy_float_range: FloatRange):
    # Check `__contains__`
    assert 12 not in dummy_float_range
    assert 50 in dummy_float_range

    # Check upper and lower bounds
    assert dummy_float_range.contains(20)
    assert dummy_float_range.contains(100)


def test_float_range_len(dummy_float_range: FloatRange):
    assert dummy_float_range.len() == 80
