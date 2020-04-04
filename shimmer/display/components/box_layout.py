"""Definition of ways to arrange Boxes."""

from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Union, Optional, Type, Iterable

import cocos
from .box import Box, BoxDefinition


@dataclass(frozen=True)
class BoxLayoutDefinition(BoxDefinition):
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

    definition_type: Type[BoxLayoutDefinition] = BoxLayoutDefinition

    def __init__(
        self,
        definition: Optional[BoxLayoutDefinition] = None,
        boxes: Optional[Iterable[Box]] = None,
    ):
        """
        Create a new BoxLayout.

        :param definition: Definition of this Layout.
        :param boxes: List of Boxes to include in the layout.
        """
        super(BoxLayout, self).__init__(definition)
        self._boxes: List[Box] = []
        self.definition: BoxLayoutDefinition = self.definition
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
        super(BoxLayout, self).remove(obj, no_resize=no_resize)
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

        # Find the tallest box so we can arrange with the center of each box aligned.
        tallest = max((box.rect.height for box in self._boxes))

        x_total = 0
        for box in self._boxes:
            box.x = x_total
            x_total += box.rect.width + self.definition.spacing
            box.y = (tallest / 2) - (box.rect.height / 2)

        self.update_rect()


class BoxColumn(BoxLayout):
    """Arranges boxes vertically. Boxes are arranged from bottom to top."""

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
            box.x = (widest / 2) - (box.rect.width / 2)

        self.update_rect()


def build_rectangular_grid(
    definition: BoxLayoutDefinition, boxes: List[Box]
) -> Union[BoxRow, BoxColumn]:
    """
    Build a rectangular grid of boxes.

    Fills from bottom-left.

    Return type is either a BoxRow of BoxColumns; or a BoxColumn of BoxRows.

    :param definition: Definition of the BoxLayout to create.
        This is passed to all of the layouts created, including the nested ones.
    :param boxes: Boxes to include.
    """
    if definition.boxes_per_row is not None:
        grid_type = BoxColumn
        element_type = BoxRow
        boxes_per_element = definition.boxes_per_row
        max_elements = definition.boxes_per_column
    elif definition.boxes_per_column is not None:
        grid_type = BoxRow
        element_type = BoxColumn
        boxes_per_element = definition.boxes_per_column
        max_elements = definition.boxes_per_row
    else:
        raise ValueError(
            "Grid layout is undefined with both `boxes_per_row` and `boxes_per_column` undefined."
        )

    # Maximum elements is one per box
    max_elements = max_elements if max_elements is not None else len(boxes)
    element_index = 0
    elements = []
    while True:
        if element_index >= max_elements:
            # Reached max requested boxes_per_row/boxes_per_column
            break

        box_batch = boxes[
            element_index * boxes_per_element : (element_index + 1) * boxes_per_element
        ]

        if not box_batch:
            # We've run out of boxes.
            # Last element might have fewer than other elements, but that's ok.
            break

        elements.append(element_type(definition, box_batch))
        element_index += 1

    return grid_type(definition, elements)


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
        return BoxRow(definition, boxes)
    elif width_height == (1, None):
        return BoxColumn(definition, boxes)
    else:
        return build_rectangular_grid(definition, boxes)
