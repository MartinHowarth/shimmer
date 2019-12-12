import cocos
import logging

from shimmer.display.data_structures import Color

from shimmer.display.primitives import create_rect, UpdatingNode
from shimmer.engine.programmable.definition import Instruction

log = logging.getLogger(__name__)


class InstructionDisplay(UpdatingNode):
    text_format = "{}"

    def __init__(self, instruction: Instruction):
        super(InstructionDisplay, self).__init__()
        self.instruction = instruction

        self.bg_color = Color(100, 100, 255)
        self.bg_color_active = Color(100, 180, 100)
        self.text_color = Color(0, 0, 0)

        self.label = cocos.text.Label(
            self.text,
            font_name="calibri",
            font_size=16,
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )
        self.width = self.label.element.content_width
        self.height = self.label.element.content_height
        self.label.position = self.width / 2, self.height / 2
        self.add(self.label)

        self.background = create_rect(
            self.label.element.content_width, self.height, self.bg_color
        )
        self.background.draw()
        self.add(self.background, z=-1)

    @property
    def text(self):
        return self.text_format.format(self.instruction.method_str())

    def _update(self, dt: float):
        if self.instruction.currently_running:
            self.background.color = self.bg_color_active.as_tuple()
            self.background._rgb = (
                self.bg_color_active.as_tuple()
            )  # workaround for https://github.com/los-cocos/cocos/issues/330
            self.background.opacity = self.bg_color_active.a
        else:
            self.background.color = self.bg_color.as_tuple()
            self.background._rgb = (
                self.bg_color.as_tuple()
            )  # workaround for https://github.com/los-cocos/cocos/issues/330
            self.background.opacity = self.bg_color.a
