import logging

from shimmer.display.data_structures import Color
from shimmer.display.primitives import create_rect
from shimmer.engine.widgets.gauge import GaugeDefinition
from shimmer.display.primitives import UpdatingNode

log = logging.getLogger(__name__)


class GaugeDisplay(UpdatingNode):
    def __init__(self, definition: GaugeDefinition):
        super(GaugeDisplay, self).__init__()
        self.definition = definition
        self.height = 100
        self.width = 10

        self.bg_color = Color(100, 100, 255)
        self.low_color = Color(255, 255, 0)
        self.high_color = Color(0, 255, 0)
        self.indicator_color = Color(50, 50, 50)
        self.indicator_height = 3

        self.init_background()
        self.indicator = create_rect(
            self.width, self.indicator_height, self.indicator_color
        )
        self.indicator.draw()
        self.add(self.indicator)

        self._indicator_last_value: float = 0.0

    def init_background(self) -> None:
        background = create_rect(self.width, self.height, self.bg_color)
        background.position = 0, 0  # Draw at origin of parent layer
        background.draw()
        self.add(background)

        low_len = int(self.definition.low_fraction_len * self.height)
        low = create_rect(self.width, low_len, self.low_color)
        low.position = 0, int(self.definition.low_fraction_start * self.height)
        low.draw()
        self.add(low)

        high_len = int(self.definition.high_fraction_len * self.height)
        high = create_rect(self.width, high_len, self.high_color)
        high.position = 0, int(self.definition.high_fraction_start * self.height)
        high.draw()
        self.add(high)

    def _current_indicator_value(self) -> float:
        return self.definition.value

    def _update(self, dt):
        self.indicator.position = (
            0,
            int(self.definition.value_fraction_start * self.height),
        )
