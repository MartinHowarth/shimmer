"""Test data structures used for display elements. These tests do not require a GUI."""

from shimmer.components.font import Calibri
from shimmer.widgets.text_box import TextBoxDefinition


def test_text_box_definition_to_pyglet_label_kwargs():
    """Test that a TextBoxDefinition is correctly converted into pyglet compatible kwargs."""
    defn = TextBoxDefinition(text="Test", font=Calibri)
    assert defn.to_pyglet_label_kwargs() == {
        "align": "left",
        "bold": False,
        "color": (255, 255, 255, 255),
        "dpi": None,
        "font_name": "calibri",
        "font_size": 16,
        "height": None,
        "italic": False,
        "text": "Test",
        "width": None,
        "multiline": False,
        "anchor_x": "left",
        "anchor_y": "bottom",
    }


def test_text_box_definition_auto_multiline(subtests):
    """Test that the multiline attribute gets set correctly on dataclass init."""
    with subtests.test("With `width` specified, multiline should be True."):
        defn = TextBoxDefinition(text="Test", font=Calibri, width=300)
        assert defn.is_multiline() is True
    with subtests.test("With no `width` specified, multiline should be False."):
        defn = TextBoxDefinition(text="Test", font=Calibri, width=None)
        assert defn.is_multiline() is False
