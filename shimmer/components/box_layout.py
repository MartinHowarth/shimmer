"""Definition of ways to arrange Boxes."""

from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Union, Optional, Type, Iterable, Tuple

import cocos
from .box import Box, BoxDefinition
from ..alignment import (
    PositionalAnchor,
    CenterCenter,
    HorizontalAlignment,
    VerticalAlignment,
)


@dataclass(frozen=True)
class BoxRowDefinition(BoxDefinition):
    """
    Definition of a row of Boxes.

    :param spacing: Pixel spacing to leave between boxes.
    :param alignment: Whether boxes should be aligned with each other at the top, center
        or bottom. Only has an impact if the boxes are of different sizes.
    """

    spacing: int = 10
    alignment: VerticalAlignment = VerticalAlignment.center


@dataclass(frozen=True)
class BoxColumnDefinition(BoxDefinition):
    """
    Definition of a column of Boxes.

    :param spacing: Pixel spacing to leave between boxes.
    :param alignment: Whether boxes should be aligned with each other on the left, center
        or right. Only has an impact if the boxes are of different sizes.
    """

    spacing: int = 10
    alignment: HorizontalAlignment = HorizontalAlignment.center


@dataclass(frozen=True)
class BoxGridDefinition(BoxDefinition):
    """
    Definition of a rectangular grid of Boxes.

    Supported layouts are:
      - single vertical column
      - single horizontal row
      - rectangular grid with multiple rows/columns

    :param spacing: Number of pixels to leave between Boxes.
        Possible types:
          - int:              Pixel spacing in both x and y directions
          - Tuple[int, int]:  Pixel spacing in (x, y) directions respectively.
    :param num_columns: If given, boxes will fill row-by-row upwards; up to a maximum of `height`.
    :param num_rows: If given and `num_columns` is not, then boxes will fill
        column-by-column from left to right with no max width.

        Examples of values of (num_columns, num_rows):
          - (None, 1) results in a single row of buttons
          - (1, None) results in a single column of buttons
          - (x, y)    results in a x by y grid of buttons
    :param alignment: A PositionalAnchor definition the point in each Box that should be aligned
        in each row or column.
    """

    spacing: Union[int, Tuple[int, int]] = 10
    num_columns: Optional[int] = None
    num_rows: Optional[int] = 1
    alignment: PositionalAnchor = CenterCenter

    @property
    def row_definition(self) -> BoxRowDefinition:
        """Definition for each row of the grid."""
        spacing = self.spacing if isinstance(self.spacing, int) else self.spacing[0]
        return BoxRowDefinition(spacing=spacing, alignment=self.alignment.vertical)

    @property
    def column_definition(self) -> BoxColumnDefinition:
        """Definition for each column of the grid."""
        spacing = self.spacing if isinstance(self.spacing, int) else self.spacing[1]
        return BoxColumnDefinition(spacing=spacing, alignment=self.alignment.horizontal)


class BoxLayoutBase(Box):
    """A collection of Boxes with a well defined layout."""

    def __init__(
        self,
        definition: Optional[BoxDefinition] = None,
        boxes: Optional[Iterable[Box]] = None,
    ):
        """
        Create a new BoxLayout.

        :param definition: Definition of this Layout.
        :param boxes: List of Boxes to include in the layout.
        """
        super(BoxLayoutBase, self).__init__(definition)
        self._boxes: List[Box] = []
        for box in boxes or []:
            self.add(box)
        self.update_layout()

    def remove(
        self, obj: Union[cocos.cocosnode.CocosNode, Box], no_resize: bool = False
    ) -> None:
        """
        Remove an object from this Layout, and update the position of other Boxes if needed.

        :param obj: CocosNode to remove.
        :param no_resize: If True, then the size of this box is not dynamically changed.
        """
        super(BoxLayoutBase, self).remove(obj, no_resize=no_resize)
        if isinstance(obj, Box):
            self._boxes.remove(obj)
            self.update_layout()

    def add(
        self,
        child: Union[cocos.cocosnode.CocosNode, Box],
        z: int = 0,
        name: Optional[str] = None,
        no_resize: bool = False,
        position: Optional[int] = None,
    ) -> None:
        """
        Add a child cocosnode. If it's a Box then include it in the layout.

        :param child: CocosNode to add.
        :param z: See CocosNode
        :param name: See CocosNode
        :param no_resize: Ignored.
        :param position: Index to insert the box into the list of boxes. Defaults to the end.
        """
        super(BoxLayoutBase, self).add(child, z, name)
        if isinstance(child, Box):
            if position is None:
                self._boxes.append(child)
            else:
                self._boxes.insert(position, child)
            self.update_layout()

    @abstractmethod
    def update_layout(self) -> None:
        """Update the position of all boxes in this Layout."""


class BoxRow(BoxLayoutBase):
    """Arranges boxes horizontally. Boxes are arranged from left to right."""

    definition_type: Type[BoxRowDefinition] = BoxRowDefinition

    def __init__(
        self,
        definition: Optional[BoxRowDefinition] = None,
        boxes: Optional[Iterable[Box]] = None,
    ):
        """
        Create a new BoxRow.

        :param definition: Definition to use to layout the boxes.
        :param boxes: The boxes to be laid out. More can be added later using `self.add(box)`.
        """
        super(BoxRow, self).__init__(definition, boxes)
        self.definition: BoxRowDefinition = self.definition

    def update_layout(self) -> None:
        """Update the position of all boxes in this Layout."""
        # Don't update layout if there are no boxes to layout.
        if not self._boxes:
            return

        # Find the tallest box so we can arrange with the center of each box aligned.
        tallest = max((box.rect.height for box in self._boxes))

        x_total = 0
        for box in self._boxes:
            box.x = x_total
            x_total += box.rect.width + self.definition.spacing
            if self.definition.alignment == VerticalAlignment.bottom:
                box.y = 0
            elif self.definition.alignment == VerticalAlignment.center:
                box.y = (tallest / 2) - (box.rect.height / 2)
            elif self.definition.alignment == VerticalAlignment.top:
                box.y = tallest - box.rect.height
            else:
                raise AssertionError(
                    f"{self.definition.alignment} "
                    f"must be a member of {VerticalAlignment}."
                )

        self.update_rect()


class BoxColumn(BoxLayoutBase):
    """Arranges boxes vertically. Boxes are arranged from bottom to top."""

    definition_type: Type[BoxColumnDefinition] = BoxColumnDefinition

    def __init__(
        self,
        definition: Optional[BoxColumnDefinition] = None,
        boxes: Optional[Iterable[Box]] = None,
    ):
        """
        Create a new BoxColumn.

        :param definition: Definition to use to layout the boxes.
        :param boxes: The boxes to be laid out. More can be added later using `self.add(box)`.
        """
        super(BoxColumn, self).__init__(definition, boxes)
        self.definition: BoxColumnDefinition = self.definition

    def update_layout(self) -> None:
        """Update the position of all boxes in this Layout."""
        # Don't update layout if there are no boxes to layout.
        if not self._boxes:
            return

        # Find the widest box so we can arrange with the center of each box aligned.
        widest = max((box.rect.width for box in self._boxes))

        y_total = 0
        for box in self._boxes:
            box.y = y_total
            y_total += box.rect.height + self.definition.spacing

            if self.definition.alignment == HorizontalAlignment.left:
                box.x = 0
            elif self.definition.alignment == HorizontalAlignment.center:
                box.x = (widest / 2) - (box.rect.width / 2)
            elif self.definition.alignment == HorizontalAlignment.right:
                box.x = widest - box.rect.width
            else:
                raise AssertionError(
                    f"{self.definition.alignment} "
                    f"must be a member of {HorizontalAlignment}."
                )

        self.update_rect()


def build_rectangular_grid(
    definition: BoxGridDefinition, boxes: List[Box]
) -> Union[BoxRow, BoxColumn]:
    """
    Build a rectangular grid of boxes.

    Fills from bottom-left.

    Return type is either a BoxRow of BoxColumns; or a BoxColumn of BoxRows.

    :param definition: Definition of the BoxLayout to create.
        This is passed to all of the layouts created, including the nested ones.
    :param boxes: Boxes to include.
    """
    grid_type: Union[Type[BoxRow], Type[BoxColumn]]
    element_type: Union[Type[BoxRow], Type[BoxColumn]]
    if definition.num_columns is not None:
        grid_type = BoxColumn
        element_type = BoxRow
        boxes_per_element = definition.num_columns
        max_elements_per_line = definition.num_rows
    elif definition.num_rows is not None:
        grid_type = BoxRow
        element_type = BoxColumn
        boxes_per_element = definition.num_rows
        max_elements_per_line = definition.num_columns
    else:
        raise ValueError(
            "Grid layout is undefined with both `num_columns` and `num_rows` undefined."
        )

    # Maximum number of grid elements per row/column is one element
    # per box to be placed in the grid.
    max_elements_per_line = (
        max_elements_per_line if max_elements_per_line is not None else len(boxes)
    )
    element_index = 0
    elements = []
    while True:
        if element_index >= max_elements_per_line:
            # Reached max requested num_columns/num_rows
            break

        box_batch = boxes[
            element_index * boxes_per_element : (element_index + 1) * boxes_per_element
        ]

        if not box_batch:
            # We've run out of boxes.
            # Last element might have fewer than other elements, but that's ok.
            break

        if element_type is BoxRow:
            elements.append(BoxRow(definition.row_definition, box_batch))
        else:
            elements.append(BoxColumn(definition.column_definition, box_batch))
        element_index += 1

    if grid_type is BoxRow:
        return BoxRow(definition.row_definition, elements)
    else:
        return BoxColumn(definition.column_definition, elements)


def create_box_layout(
    definition: BoxGridDefinition, boxes: List[Box]
) -> Union[BoxRow, BoxColumn]:
    """
    Create a layout of boxes based on the given definition.

    :param definition: BoxGridDefinition to use.
    :param boxes: Boxes to include in the layout.
    :return: BowRow or BoxColumn containing the given boxes.
    """
    width_height = definition.num_columns, definition.num_rows
    if width_height == (None, 1):
        return BoxRow(definition.row_definition, boxes)
    elif width_height == (1, None):
        return BoxColumn(definition.column_definition, boxes)
    else:
        return build_rectangular_grid(definition, boxes)
