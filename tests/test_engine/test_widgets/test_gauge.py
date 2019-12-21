"""Tests for the gauge widget."""

import pytest

from shimmer.engine.widgets.gauge import GaugeDefinition, FloatRange


@pytest.fixture
def dummy_gauge_definition():
    """Common gauge definition for use in these tests."""
    return GaugeDefinition(
        FloatRange(0, 100), FloatRange(20, 80), FloatRange(50, 75), 40,
    )


def test_fraction_calculations(dummy_gauge_definition: GaugeDefinition) -> None:
    """Test fractions of the gauge calculations."""
    assert dummy_gauge_definition.low_fraction_start == 0.2
    assert dummy_gauge_definition.high_fraction_start == 0.5
    assert dummy_gauge_definition.value_fraction_start == 0.4
    assert dummy_gauge_definition.low_fraction_len == 0.6
    assert dummy_gauge_definition.high_fraction_len == 0.25


def test_changing_value(dummy_gauge_definition: GaugeDefinition) -> None:
    """Test changing value of the gauge is handled correctly."""
    # Ensure value_fraction_start is updated
    assert dummy_gauge_definition.value_fraction_start == 0.4
    dummy_gauge_definition.value = 20
    assert dummy_gauge_definition.value_fraction_start == 0.2

    # Make sure low bound is respected
    dummy_gauge_definition.value = -100
    assert dummy_gauge_definition.value == 0

    # Make sure upper bound is respected
    dummy_gauge_definition.value = 1000
    assert dummy_gauge_definition.value == 100
