"""Test the various box layout methods."""
import pytest

import cocos
from shimmer.alignment import VerticalAlignment, HorizontalAlignment
from shimmer.components.box import BoxDefinition, Box
from shimmer.components.box_layout import (
    BoxRow,
    BoxColumn,
    BoxGridDefinition,
    BoxRowDefinition,
    BoxColumnDefinition,
    create_box_layout,
)
from shimmer.data_structures import Color
from shimmer.widgets.button import ButtonDefinition


def make_visible_button_definition(
    text: str, width: int, height: int
) -> ButtonDefinition:
    """Create a ButtonDefinition with the given text."""
    return ButtonDefinition(
        text=text,
        base_color=Color(0, 120, 255),
        depressed_color=Color(0, 80, 255),
        hover_color=Color(0, 200, 255),
        width=width,
        height=height,
    )


def test_box_row(mock_gui):
    """Test arranging boxes in a horizontal row."""
    boxes = [Box(BoxDefinition(width=10 * i, height=100)) for i in range(1, 5)]

    box_row = BoxRow(BoxRowDefinition(spacing=10), boxes)
    assert box_row.rect.width == 130
    assert box_row.rect.height == 100
    assert box_row.bounding_rect_of_children() == cocos.rect.Rect(0, 0, 130, 100)

    assert boxes[0].position == (0, 0)
    assert boxes[1].position == (20, 0)
    assert boxes[2].position == (50, 0)
    assert boxes[3].position == (90, 0)


@pytest.mark.parametrize(
    "alignment",
    [VerticalAlignment.bottom, VerticalAlignment.center, VerticalAlignment.top,],
)
def test_box_row_with_different_height_boxes(mock_gui, alignment):
    """Test arranging boxes of various heights in a horizontal row."""
    boxes = [Box(BoxDefinition(width=40, height=10 * i)) for i in range(1, 5)]

    box_row = BoxRow(BoxRowDefinition(spacing=10, alignment=alignment), boxes)
    assert box_row.rect.width == 190
    assert box_row.rect.height == 40
    assert box_row.bounding_rect_of_children() == cocos.rect.Rect(0, 0, 190, 40)

    if alignment == VerticalAlignment.bottom:
        assert boxes[0].position == (0, 0)
        assert boxes[1].position == (50, 0)
        assert boxes[2].position == (100, 0)
        assert boxes[3].position == (150, 0)
    elif alignment == VerticalAlignment.center:
        assert boxes[0].position == (0, 15)
        assert boxes[1].position == (50, 10)
        assert boxes[2].position == (100, 5)
        assert boxes[3].position == (150, 0)
    elif alignment == VerticalAlignment.top:
        assert boxes[0].position == (0, 30)
        assert boxes[1].position == (50, 20)
        assert boxes[2].position == (100, 10)
        assert boxes[3].position == (150, 0)
    else:
        assert False, "Alignment was not a valid value."


def test_box_column(mock_gui):
    """Test arranging boxes in a vertical column."""
    boxes = [Box(BoxDefinition(width=100, height=10 * i)) for i in range(1, 5)]

    box_column = BoxColumn(BoxColumnDefinition(spacing=10), boxes)
    assert box_column.rect.width == 100
    assert box_column.rect.height == 130
    assert box_column.bounding_rect_of_children() == cocos.rect.Rect(0, 0, 100, 130)

    assert boxes[0].position == (0, 0)
    assert boxes[1].position == (0, 20)
    assert boxes[2].position == (0, 50)
    assert boxes[3].position == (0, 90)


@pytest.mark.parametrize(
    "alignment",
    [HorizontalAlignment.left, HorizontalAlignment.center, HorizontalAlignment.right,],
)
def test_box_column_with_different_width_boxes(mock_gui, alignment):
    """Test arranging boxes of various widths in a vertical column."""
    boxes = [Box(BoxDefinition(width=10 * i, height=40)) for i in range(1, 5)]

    box_column = BoxColumn(BoxColumnDefinition(spacing=10, alignment=alignment), boxes)
    assert box_column.rect.width == 40
    assert box_column.rect.height == 190
    assert box_column.bounding_rect_of_children() == cocos.rect.Rect(0, 0, 40, 190)

    if alignment == HorizontalAlignment.left:
        assert boxes[0].position == (0, 0)
        assert boxes[1].position == (0, 50)
        assert boxes[2].position == (0, 100)
        assert boxes[3].position == (0, 150)
    elif alignment == HorizontalAlignment.center:
        assert boxes[0].position == (15, 0)
        assert boxes[1].position == (10, 50)
        assert boxes[2].position == (5, 100)
        assert boxes[3].position == (0, 150)
    elif alignment == HorizontalAlignment.right:
        assert boxes[0].position == (30, 0)
        assert boxes[1].position == (20, 50)
        assert boxes[2].position == (10, 100)
        assert boxes[3].position == (0, 150)
    else:
        assert False, "Alignment was not a valid value."


@pytest.mark.parametrize(
    "definition,num_boxes,exp_outer_type,exp_outer,exp_inner",
    [
        pytest.param(
            BoxGridDefinition(num_columns=None, num_rows=1),
            10,
            BoxRow,
            1,
            10,
            id="One row",
        ),
        pytest.param(
            BoxGridDefinition(num_columns=1, num_rows=None),
            10,
            BoxColumn,
            1,
            10,
            id="One column",
        ),
        pytest.param(
            BoxGridDefinition(num_columns=2, num_rows=None),
            10,
            BoxColumn,
            2,
            5,
            id="2 columns",
        ),
        pytest.param(
            BoxGridDefinition(num_columns=10, num_rows=None),
            10,
            BoxColumn,
            10,
            1,
            id="Max columns (10)",
        ),
        pytest.param(
            BoxGridDefinition(num_columns=None, num_rows=10),
            10,
            BoxRow,
            10,
            1,
            id="Max rows (10)",
        ),
    ],
)
def test_create_box_layout(
    mock_gui, definition, num_boxes, exp_outer_type, exp_outer, exp_inner
):
    """Test creating various box layouts."""
    boxes = [Box(BoxDefinition(width=10, height=10)) for _ in range(num_boxes)]
    box_layout = create_box_layout(definition, boxes)

    first_child = box_layout.get_children()[0]
    assert isinstance(box_layout, exp_outer_type)

    if exp_outer * exp_inner > num_boxes:
        # Enough boxes to need two rows or columns to contain them.
        if exp_outer_type is BoxColumn:
            assert isinstance(first_child, BoxRow)
        else:
            assert isinstance(first_child, BoxColumn)
        assert len(box_layout.get_children()) == exp_outer
        assert len(first_child.get_children()) == exp_inner
    else:
        # Only a single BoxRow or BoxColumn
        assert len(box_layout.get_children()) == exp_inner
        assert isinstance(first_child, Box)
