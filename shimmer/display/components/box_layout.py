"""Definition of ways to arrange Boxes."""

import cocos

from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Union, Optional

from .box import Box


@dataclass(frozen=True)
class BoxLayoutDefinition:
    """
    Definition of a layout of Boxes.

    Supported layouts are:
      - vertically column
      - horizontal row
      - rectangular grid

    :param spacing: Number of pixels to leave between Boxes.
    :param boxes_per_row: If given, boxes will fill row-by-row upwards; up to a maximum of `height`.
    :param boxes_per_column: If given and `boxes_per_row` is not, then boxes will fill
        column-by-column from left to right with no max width.

        Examples of values of (boxes_per_row, boxes_per_column):
          - (None, 1) results in a single row of buttons
          - (1, None) results in a single column of buttons
          - (x, y)    results in a x by y grid of buttons
    """

    spacing: int = 10
    boxes_per_row: Optional[int] = None
    boxes_per_column: Optional[int] = 1


class BoxLayout(Box):
    """A collection of Boxes with a well defined layout."""

    def __init__(self, boxes: List[Box], spacing: int = 10):
        """
        Create a new BoxLayout.

        :param boxes: List of Boxes to include in the layout.
        :param spacing: Number of pixels to leave between Boxes.
        """
        super(BoxLayout, self).__init__()
        self._boxes = []  # type: List[Box]
        self._spacing = spacing
        for box in boxes:
            self.add(box)
        self.update_layout()

    @property
    def spacing(self) -> int:
        """Return the spacing between items in the layout."""
        return self._spacing

    @spacing.setter
    def spacing(self, value: int) -> None:
        """Set the spacing between items in the layout, and update the layout."""
        self._spacing = value
        self.update_layout()

    def remove(self, obj: Union[cocos.cocosnode.CocosNode, Box]) -> None:
        """
        Remove an object from this Layout, and update the position of other Boxes if needed.

        :param obj: CocosNode to remove.
        """
        super(BoxLayout, self).remove(obj)
        if isinstance(obj, Box):
            self._boxes.remove(obj)
            self.update_layout()

    def add(
        self,
        child: Union[cocos.cocosnode.CocosNode, Box],
        z: int = 0,
        name: Optional[str] = None,
        position: Optional[int] = None,
    ) -> None:
        """
        Add a child cocosnode. If it's a Box then include it in the layout.

        :param child: CocosNode to add.
        :param z: See CocosNode
        :param name: See CocosNode
        :param position: Index to insert the box into the list of boxes. Defaults to the end.
        """
        super(BoxLayout, self).add(child, z, name)
        if isinstance(child, Box):
            if position is None:
                self._boxes.append(child)
            else:
                self._boxes.insert(position, child)
            self.update_layout()

    @abstractmethod
    def update_layout(self) -> None:
        """Update the position of all boxes in this Layout."""
        pass


class BoxRow(BoxLayout):
    """Arranges boxes horizontally. Boxes are arranged from left to right."""

    def update_layout(self) -> None:
        """Update the position of all boxes in this Layout."""
        # Don't update layout if there are no boxes to layout.
        if not self._boxes:
            return

        x_total = 0
        for box in self._boxes:
            box.x = x_total
            x_total += box.rect.width + self._spacing
        height = max([box.rect.height for box in self._boxes])
        width = sum((box.rect.width for box in self._boxes)) + self._spacing * (
            len(self._boxes) - 1
        )
        self.set_size(width, height)


class BoxColumn(BoxLayout):
    """Arranges boxes vertically. Boxes are arranged from bottom to top."""

    def update_layout(self) -> None:
        """Update the position of all boxes in this Layout."""
        # Don't update layout if there are no boxes to layout.
        if not self._boxes:
            return

        y_total = 0
        for box in self._boxes:
            box.y = y_total
            y_total += box.rect.height + self._spacing
        width = max([box.rect.width for box in self._boxes])
        height = sum((box.rect.height for box in self._boxes)) + self._spacing * (
            len(self._boxes) - 1
        )
        self.set_size(width, height)


def build_rectangular_grid(
    boxes: List[Box],
    width: Optional[int] = None,
    height: Optional[int] = None,
    spacing: int = 10,
) -> Union[BoxRow, BoxColumn]:
    """
    Build a rectangular grid of boxes.

    Fills from bottom-left.

    Return type is either a BoxRow of BoxColumns; or a BoxColumn of BoxRows.

    :param boxes: Boxes to include.
    :param width: If given, boxes will fill row-by-row upwards; up to a maximum of `height`.
    :param height: If given and `width` is not, then boxes will fill column-by-column from
        left to right with no max width.
    :param spacing: The spacing between the boxes.
    :return: Returns a BoxRow or BoxColumn depending on the stacking order.
    """
    if width is not None:
        grid_type = BoxColumn
        element_type = BoxRow
        boxes_per_element = width
        max_elements = height
    elif height is not None:
        grid_type = BoxRow
        element_type = BoxColumn
        boxes_per_element = height
        max_elements = width
    else:
        raise ValueError(
            "Grid layout is undefined with both `width` and `height` undefined."
        )

    # Maximum elements is one per box
    max_elements = max_elements if max_elements is not None else len(boxes)
    element_index = 0
    elements = []
    while True:
        if element_index >= max_elements:
            # Reached max requested width/height
            break

        box_batch = boxes[
            element_index * boxes_per_element : (element_index + 1) * boxes_per_element
        ]

        if not box_batch:
            # We've run out of boxes.
            # Last element might have fewer than other elements, but that's ok.
            break

        elements.append(element_type(box_batch, spacing=spacing))
        element_index += 1

    return grid_type(elements, spacing=spacing)


def create_box_layout(
    definition: BoxLayoutDefinition, boxes: List[Box]
) -> Union[BoxRow, BoxColumn]:
    """
    Create a layout of boxes based on the given definition.

    :param definition: BoxLayoutDefinition to use.
    :param boxes: Boxes to include in the layout.
    :return: BowRow or BoxColumn containing the given boxes.
    """
    width_height = definition.boxes_per_row, definition.boxes_per_column
    if width_height == (None, 1):
        return BoxRow(boxes, definition.spacing)
    elif width_height == (1, None):
        return BoxColumn(boxes, definition.spacing)
    else:
        return build_rectangular_grid(
            boxes,
            definition.boxes_per_row,
            definition.boxes_per_column,
            definition.spacing,
        )
