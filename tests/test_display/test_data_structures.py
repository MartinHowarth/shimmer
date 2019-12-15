"""Test data structures used for display elements. These tests do not require a GUI."""

from shimmer.display.data_structures import (
    LabelDefinition,
    Calibri,
)


def test_label_definition_to_pyglet_label_kwargs():
    """No GUI. Test that a LabelDefinition is correctly converted into pyglet compatible kwargs."""
    defn = LabelDefinition(text="Test", font=Calibri)
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
        "width": 300,
        "multiline": True,
        "anchor_x": "left",
        "anchor_y": "bottom",
    }


def test_label_definition_auto_multiline(subtests):
    """No GUI. Test that the multiline attribute gets set correctly on dataclass init."""
    with subtests.test("With `width` specified, multiline should be True."):
        defn = LabelDefinition(text="Test", font=Calibri, width=300)
        assert defn.multiline is True
    with subtests.test("With no `width` specified, multiline should be False."):
        defn = LabelDefinition(text="Test", font=Calibri, width=None)
        assert defn.multiline is False
