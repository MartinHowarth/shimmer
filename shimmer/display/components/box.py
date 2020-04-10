"""
Definition of the Box primitive.

A Box is a CocosNode that defines an area.
"""

import logging
from dataclasses import dataclass, fields, replace
from enum import Enum, auto
from typing import Optional, Type, Iterable, Tuple, Union

import cocos
from ..alignment import (
    ZIndexEnum,
    PositionalAnchor,
    CenterCenter,
)
from ..data_structures import Color
from ..primitives import create_color_rect

log = logging.getLogger(__name__)


class DynamicSizeBehaviourEnum(Enum):
    """
    Enum of options for dynamically sized boxes.

    fit_children - Box size encompasses all of its children in both dimensions.
    match_parent - Box size matches parent size.
    """

    fit_children = auto()
    match_parent = auto()


@dataclass(frozen=True)
class BoxDefinition:
    """Common definition to all Boxes."""

    # If either `width` or `height` are None then the box size will be set dynamically
    # based on the value of `dynamic_size_behaviour`.
    # Set to 0 to match the entire window size.
    width: Optional[int] = None
    height: Optional[int] = None

    dynamic_size_behaviour: DynamicSizeBehaviourEnum = DynamicSizeBehaviourEnum.fit_children

    background_color: Optional[Color] = None

    def __str__(self) -> str:
        """String representation that excludes fields that have their default value."""
        params = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if hasattr(value, "__name__"):
                # Don't recurse into getting the string representation of methods, as these
                # are often bound methods and result in calling back into this function.
                value = value.__name__

            if value != field.default:
                params[field.name] = str(value)
        return f"{self.__class__.__name__}({params})"

    @property
    def is_dynamic_width(self) -> bool:
        """True if the defined Box should have dynamic width, otherwise False."""
        return self.width is None

    @property
    def is_dynamic_height(self) -> bool:
        """True if the defined Box should have dynamic height, otherwise False."""
        return self.height is None

    @property
    def is_dynamic_sized(self) -> bool:
        """True if the defined Box should have dynamic size, otherwise False."""
        return self.is_dynamic_width or self.is_dynamic_height

    @property
    def size_matches_parent(self) -> bool:
        """True if the defined Box should match the size of its parent, otherwise False."""
        return self.dynamic_size_behaviour == DynamicSizeBehaviourEnum.match_parent

    @property
    def size_fits_children(self) -> bool:
        """True if the defined Box should match the size of its children, otherwise False."""
        return self.dynamic_size_behaviour == DynamicSizeBehaviourEnum.fit_children


class Box(cocos.cocosnode.CocosNode):
    """A CocosNode that has a defined rectangular area."""

    definition_type: Type[BoxDefinition] = BoxDefinition

    def __init__(self, definition: Optional[BoxDefinition] = None):
        """Creates a new Box."""
        super(Box, self).__init__()
        if definition is None:
            definition = self.definition_type()

        self.definition = definition
        self._width: int = 0
        self._height: int = 0
        self._calculate_current_size()
        self._rect = cocos.rect.Rect(0, 0, self._width, self._height)

        self._background: Optional[cocos.layer.ColorLayer] = None
        self.update_background()

    def __repr__(self):
        """String representation of this Box."""
        return f"{self.__class__.__name__}({self.definition})"

    def __str__(self):
        """String representation of this Box."""
        return (
            f"[{id(self)}][{self.world_rect}] {repr(self)} "
            f"child of <{repr(self.parent)}>"
        )

    def contains_coord(self, x: int, y: int) -> bool:
        """Returns whether the point (x,y) is inside the box."""
        p = self.point_to_local((x, y))
        return self.rect.contains(p.x, p.y)

    @property
    def rect(self) -> cocos.rect.Rect:
        """
        Return the rect that this box encompasses.

        This rect is in the parent coordinate space.
        """
        return self._rect

    @property
    def world_rect(self) -> cocos.rect.Rect:
        """Get the rect for this Box in world coordinate space."""
        return cocos.rect.Rect(
            *self.point_to_world((0, 0)), self.rect.width, self.rect.height
        )

    def _calculate_current_size(self) -> None:
        """
        Calculate what the size of this box should be.

        This takes into account any dynamic settings in the definition.

        This updates `self._width` and `self._height`, but does not change `self.rect`.
        """
        if not self.definition.is_dynamic_sized:
            self._width = self.definition.width or 0
            self._height = self.definition.height or 0
        else:
            if self.definition.size_fits_children:
                dynamic_rect = self.bounding_rect_of_children()
            elif self.definition.size_matches_parent:
                if self.parent is not None and isinstance(self.parent, Box):
                    dynamic_rect = self.parent.rect
                else:
                    log.debug(f"Cannot match size to non-existent or non-Box parent.")
                    dynamic_rect = cocos.rect.Rect(0, 0, 0, 0)
            else:
                raise ValueError(
                    f"{self.definition.dynamic_size_behaviour} "
                    f"must be a member of `DynamicSizeBehaviourEnum`."
                )

            if self.definition.is_dynamic_width:
                self._width = dynamic_rect.width
            else:
                self._width = self.definition.width or 0

            if self.definition.is_dynamic_height:
                self._height = dynamic_rect.height
            else:
                self._height = self.definition.height or 0

    def update_rect(self):
        """
        Update the cached rect definition.

        If the rect size changes, then `on_size_change` will be called.
        """
        self._calculate_current_size()

        # If the new size is different to the old size, then handle size change.
        if self._width != self._rect.width or self._height != self._rect.height:
            self._rect.set_size((self._width, self._height))
            self.on_size_change()

    def on_size_change(self):
        """
        Called when the size of the Box changes.

        Called automatically for dynamically sized Boxes when its children change size.

        For manually resized boxes, `update_rect` should be called first, which will trigger this
        function.
        """
        self.update_background()
        if isinstance(self.parent, Box):
            self.parent.on_child_size_changed()
        for child in self.get_children():
            if isinstance(child, Box):
                child.on_parent_size_changed()

    def on_child_size_changed(self):
        """
        Called when a child of this Box changes size.

        Triggers this Box to update its size if it is dynamically sized.
        """
        self.update_rect()

    def on_parent_size_changed(self):
        """
        Called when the parent of this Box changes size.

        Triggers this Box to update its size if it is dynamically sized.
        """
        self.update_rect()

    def add(
        self,
        child: cocos.cocosnode.CocosNode,
        z: int = 0,
        name: Optional[str] = None,
        no_resize: bool = False,
    ) -> None:
        """
        Add a child to this Box. See CocosNode for parameter arguments.

        When adding a child, check for updating dynamic size of this Box.

        :param child: CocosNode to add.
        :param z: See CocosNode
        :param name: See CocosNode
        :param no_resize: If True, then the size of this box is not dynamically changed.
        """
        super(Box, self).add(child, z, name)
        if self.definition.is_dynamic_sized and not no_resize:
            self.update_rect()

        # Notify all children that the parent size may have changed.
        # This also handles dynamic children who need to set their size for the first time.
        for child in self.get_children():
            if isinstance(child, Box):
                child.on_parent_size_changed()

    def remove(self, child: cocos.cocosnode.CocosNode, no_resize: bool = False) -> None:
        """
        Remove a child from this Box. See CocosNode for parameter arguments.

        When removing a child, check for updating dynamic size of this Box.

        :param child: CocosNode to remove.
        :param no_resize: If True, then the size of this box is not dynamically changed.
        """
        super(Box, self).remove(child)
        if self.definition.is_dynamic_sized and not no_resize:
            self.update_rect()

    def get_z_value(self) -> Optional[int]:
        """
        Get the z value of this Box in its parents children list.

        Returns None if this child has no parent.

        Raises ValueError if this child is not a child of parent (should never happen).
        """
        if self.parent is None:
            return None

        for z, child in self.parent.children:
            if child is self:
                return z
        raise ValueError(f"{self} is not a child of its parent.")

    def set_z_value(self, z: Union[int, ZIndexEnum]) -> None:
        """
        Set the z value of this box in its parents list of children.

        The z value controls ordering of drawing, and ordering of event handling.

        Higher z means:
          - Drawn on top of lower z nodes.
          - Receives events first (and therefore may stop them propagating to lower z nodes)
                Note: This happens because in ActiveBox we push own events before children do.

        Warning: This removes and re-adds this node to the parent, so `on_exit` and `on_enter`
            are called.
            For ActiveBoxes this will remove and re-add it to the event stack. So if the z value
            is changed during an event callback, the event may skip children of THIS node.
            This can be worked around by consuming the event when changing the Z value, and
            re-dispatching it (see FocusBox for an example of this).

        :param z: Int or member of ZIndexEnum to set the z value to.
        """
        if z is ZIndexEnum.top:
            # Children are in z order from lowest to highest, so highest z is the last one.
            # Children are stored as the tuple (z, node)
            if self.parent.children[-1][1] is self:
                # If this box is already at the top, then do nothing.
                return
            z = self.parent.children[-1][0] + 1
        elif z is ZIndexEnum.bottom:
            # Children are in z order from lowest to highest, so lowest z is the first one.
            # Children are stored as the tuple (z, node)
            if self.parent.children[0][1] is self:
                # If this box is already at the top, then do nothing.
                return
            z = self.parent.children[0][0] - 1

        # Remove and re-add to insert this node in the child list correctly, and perform
        # `on_exit` and `on_enter` to make sure that the node is in the correct place in the
        # event stack.
        self.parent.remove(self)
        self.parent.add(self, z=z)

    def update_background(self) -> None:
        """
        Re-create the background of this Box to take account of changed size or color.

        If the background color is None, then the background is removed.
        """
        # Remove the old background
        if self._background is not None:
            self.remove(self._background, no_resize=True)

        if self.definition.background_color is None:
            return

        if self._width > 0 and self._height > 0:
            self._background = create_color_rect(
                self._width, self._height, self.definition.background_color
            )
            self._background.position = (0, 0)
            self.add(self._background, z=-100, no_resize=True)

    def _set_background_color(self, color: Color) -> None:
        """Set the color of the background of this box to the given Color."""
        self.definition = replace(self.definition, background_color=color)
        if self._background is not None:
            self._background.color = color.as_tuple()
            self._background.opacity = color.a
        else:
            self.update_background()

    def get_coordinates_of_anchor(self, anchor: PositionalAnchor) -> cocos.draw.Point2:
        """
        Get the (x, y) coordinate of the given anchor point in this Box.

        :param anchor: The anchor to get the position of.
        :return: cocos.draw.Point2 of the anchor position.
        """
        return anchor.get_coord_in_rect(self._width, self._height)

    def vector_between_anchors(
        self,
        other: "Box",
        other_anchor: PositionalAnchor,
        self_anchor: PositionalAnchor,
    ) -> cocos.draw.Vector2:
        """
        Get the vector between the anchor of this box, and the anchor of the other box.

        See `align_anchor_with_other_anchor` for argument descriptions.
        """
        if not self.is_running:
            # We need to work in a common coordinate space. The easiest choice is the director.
            # We could check for the director as an ancestor; but it is sufficient to check that
            # the Box is running (i.e. in the current scene).
            #
            # If this Box is not in the scene, then we cannot calculate relative positioning
            # reliably. However, it still works accurately for Boxes that are being aligned
            # with their parent or with siblings. Therefore only log rather than error out.
            log.debug(
                f"This Box is not in the scene, "
                f"so setting relative positioning may by unstable. {self=}, {other=}"
            )

        # Get the anchor coordinates in each Boxes coordinate space.
        self_point = self.get_coordinates_of_anchor(self_anchor)
        other_point = other.get_coordinates_of_anchor(other_anchor)

        # Translate those coordinates into the world coordinate space to ensure a common
        # coordinate space.
        self_world_point = self.point_to_world(self_point)
        other_world_point = other.point_to_world(other_point)

        # Get the difference between those two points in world space, which is the amount we need
        # to translate this Box by to align the two anchors.
        anchor_vector = other_world_point - self_world_point
        return anchor_vector

    def align_anchor_with_other_anchor(
        self,
        other: "Box",
        other_anchor: PositionalAnchor = CenterCenter,
        self_anchor: Optional[PositionalAnchor] = None,
        spacing: Union[int, Tuple[int, int], cocos.draw.Point2] = 0,
    ) -> None:
        """
        Set an anchor of this Box to be aligned an anchor of the other Box.

        For example, to align the right edge of this box with the left edge of the other:

            self.align_anchor_with_other_anchor(other, RightCenter, LeftCenter)

        :param other: The Box to align this one with.
        :param other_anchor: The anchor point of the other Box to align.
            Defaults to CenterCenter.
        :param self_anchor: The anchor point of this Box to align.
            Defaults to match `other_anchor`.
        :param spacing: Pixels to leave between the anchors.
            If an `int` is given, the direction of the spacing the vector defined between the
                given self_anchor and the CenterCenter of this Box.
                Positive integers serve to make more space between the edges of the two Boxes,
                while negative integers serve to cause the Box edges to overlap.
            If a Tuple[int, int] is given, then it is treated as an exact (x, y) offset.
        """
        if self_anchor is None:
            self_anchor = other_anchor

        anchor_vector = self.vector_between_anchors(other, other_anchor, self_anchor)

        # Now account for spacing.
        # If the spacing is an integer, then it is applied in the direction defined from
        # the given self_anchor to the CenterCenter of this Box.
        if isinstance(spacing, (cocos.draw.Point2, cocos.draw.Vector2)):
            spacing_vector = spacing
        elif isinstance(spacing, tuple):
            spacing_vector = cocos.draw.Point2(*spacing)
        else:
            # spacing is an int
            if spacing == 0 or self_anchor == CenterCenter:
                spacing_vector = cocos.draw.Point2(0, 0)
            else:
                spacing_vector = self.get_coordinates_of_anchor(
                    CenterCenter
                ) - self.get_coordinates_of_anchor(self_anchor)
                spacing_vector.normalize()
                spacing_vector *= spacing

        self.position += anchor_vector + spacing_vector

    def bounding_rect_of_children(self) -> cocos.rect.Rect:
        """
        Return the rect that contains all the child (and grandchild etc.) Boxes of this Box.

        The Rect of this Box is not taken into account.

        The bottom-left corner of the returned rect is aligned with the origin of this Box.
        """

        def get_world_rect(
            node: cocos.cocosnode.CocosNode,
        ) -> Optional[cocos.rect.Rect]:
            if isinstance(node, Box) and node is not self:
                node_rect = node.world_rect
                # If the box dynamically matches parent, then ignore the size of it.
                if node.definition.size_matches_parent:
                    if node.definition.is_dynamic_width:
                        node_rect.width = 0
                    if node.definition.is_dynamic_height:
                        node_rect.height = 0
                return node_rect
            return None

        world_rects = list(filter(lambda x: x is not None, self.walk(get_world_rect)))
        if len(world_rects) != 0:
            bounding_world_rect = bounding_rect_of_rects(world_rects)
            bounding_local_rect = cocos.rect.Rect(
                *self.point_to_local(bounding_world_rect.position),
                bounding_world_rect.width,
                bounding_world_rect.height,
            )
        else:
            bounding_local_rect = cocos.rect.Rect(0, 0, 0, 0)

        return bounding_local_rect


class ActiveBox(Box):
    """A Box that adds itself to the cocos director event handlers when entering the scene."""

    def on_enter(self):
        """Called every time just before the node enters the stage."""
        # Deliberately push handlers for this node before calling for sub nodes. This causes
        # handlers for children to be inserted higher in the stack than their parents,
        # resulting in them getting higher priority on handling events.
        # This makes sense because children are generally smaller / drawn on top of parents.
        cocos.director.director.window.push_handlers(self)
        super(ActiveBox, self).on_enter()

    def on_exit(self):
        """Called every time just before the node exits the stage."""
        cocos.director.director.window.remove_handlers(self)
        super(ActiveBox, self).on_exit()


def bounding_rect_of_rects(rects: Iterable[cocos.rect.Rect]) -> cocos.rect.Rect:
    """Return the minimal rect needed to cover all the given rects."""
    lefts, rights, tops, bottoms = zip(
        *((rect.x, rect.x + rect.width, rect.y + rect.height, rect.y) for rect in rects)
    )

    left = min(lefts)
    bottom = min(bottoms)
    right = max(rights)
    top = max(tops)

    x = min(left, right)
    y = min(bottom, top)
    width = max(left, right) - x
    height = max(bottom, top) - y

    return cocos.rect.Rect(x, y, width, height)
