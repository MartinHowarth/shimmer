import cocos

from shimmer.display.data_structures import Color
from shimmer.display.components.button import (
    VisibleButtonDefinition,
    VisibleButton,
)
from shimmer.display.components.box_layout import (
    BoxRow,
    BoxColumn,
    build_rectangular_grid,
)


def make_visible_button_definition(text: str):
    return VisibleButtonDefinition(
        text=text,
        base_color=Color(0, 120, 255),
        depressed_color=Color(0, 80, 255),
        hover_color=Color(0, 200, 255),
    )


def test_box_row(run_gui):
    """Horizontal row of buttons should be shown."""
    buttons = []
    for ind in range(4):
        btn = VisibleButton(make_visible_button_definition(str(ind)))
        btn.rect = cocos.rect.Rect(0, 0, 40, 100)
        buttons.append(btn)

    box_row = BoxRow(buttons, spacing=10)
    assert box_row.rect.height == 100
    assert box_row.rect.width == 190

    assert run_gui(test_box_row, box_row)


def test_box_column(run_gui):
    """Vertical column of buttons should be shown."""
    buttons = []
    for ind in range(4):
        btn = VisibleButton(make_visible_button_definition(str(ind)))
        btn.rect = cocos.rect.Rect(0, 0, 100, 40)
        buttons.append(btn)

    box_column = BoxColumn(buttons)
    assert box_column.rect.width == 100
    assert box_column.rect.height == 190

    assert run_gui(test_box_column, box_column)


def test_build_rectangular_grid_horizontal(run_gui):
    """Rectangular grid of buttons should be shown, with only 2 on the top row."""
    n_buttons = 10
    buttons = []
    for ind in range(n_buttons):
        btn = VisibleButton(make_visible_button_definition(str(ind)))
        btn.rect = cocos.rect.Rect(0, 0, 100, 40)
        buttons.append(btn)

    box_grid = build_rectangular_grid(buttons, width=4)

    assert box_grid.rect.width == 430
    assert box_grid.rect.height == 140

    assert run_gui(test_build_rectangular_grid_horizontal, box_grid)
