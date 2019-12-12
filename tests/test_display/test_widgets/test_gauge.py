import pytest

from shimmer.engine.widgets.base import FloatRange
from shimmer.engine.widgets.gauge import GaugeDefinition
from shimmer.display.widgets.gauge import GaugeDisplay


@pytest.fixture
def dummy_gauge_definition():
    return GaugeDefinition(
        "test", FloatRange(0, 100), FloatRange(20, 80), FloatRange(50, 75), 40,
    )


def test_gauge_display(run_gui, dummy_gauge_definition):
    """A gauge should be shown with a static indicator value."""
    layer = GaugeDisplay(dummy_gauge_definition)
    assert run_gui(test_gauge_display, layer)


def test_gauge_display_dynamic(run_gui, dummy_gauge_definition):
    """A gauge should be shown with a steadily increasing indicator value, wrapping at max."""

    class LoopingGaugeDisplay(GaugeDisplay):
        def _update(self, dt):
            self.definition.value += 1
            self.definition.value %= self.definition.full_range.max
            super(LoopingGaugeDisplay, self)._update(dt)

    layer = LoopingGaugeDisplay(dummy_gauge_definition)
    assert run_gui(test_gauge_display_dynamic, layer)
