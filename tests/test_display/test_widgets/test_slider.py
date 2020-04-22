"""Tests for the slider widget."""
from shimmer.widgets.slider import Slider, SliderDefinition, OrientationEnum

# TODO test slider with mock gui
# TODO test graduations
def test_slider(run_gui, updatable_text_box):
    """A slider should be shown and the current value should update as it is changed."""
    text_box, update_text_box = updatable_text_box

    slider = Slider(SliderDefinition(width=40, height=200, on_change=update_text_box))

    assert run_gui(test_slider, slider, text_box)


def test_slider_horizontal(run_gui, updatable_text_box):
    """A slider should be shown and the current value should update as it is changed."""
    text_box, update_text_box = updatable_text_box

    slider = Slider(
        SliderDefinition(
            width=200,
            height=40,
            on_change=update_text_box,
            orientation=OrientationEnum.horizontal,
        )
    )

    assert run_gui(test_slider_horizontal, slider, text_box)
