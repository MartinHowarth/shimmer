import logging
from dataclasses import dataclass, field
from typing import Optional

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class ItemDefinition:
    id: str
    name: str
    max_stack_size: int = 1

    @property
    def is_stackable(self) -> bool:
        return self.max_stack_size > 1


@dataclass
class Item:
    definition: ItemDefinition
    stack_size: int
    _stack_size: int = field(init=False, repr=False)

    @property
    def stack_size(self) -> int:
        return self._stack_size

    @stack_size.setter
    def stack_size(self, value: int) -> None:
        if value > self.definition.max_stack_size:
            raise ValueError(
                f"stack_size={value} cannot be greater than {self.definition.max_stack_size}."
            )
        if value < 0:
            raise ValueError(f"stack_size={value} cannot be negative.")
        self._stack_size = value

    def receive_merge(self, other: "Item") -> Optional["Item"]:
        """
        Merge an item into this item.

        Serves to move as many items from the "other" item stack into this item stack.

        :param other: The item to merge.
        :return: None if the item stack was fully merged into this item stack. Otherwise return
            the same item object back but with `stack_size` reduced by as many items as would
            fit into this item stack.
        """
        if other.definition != self.definition:
            return other

        can_accept = self.definition.max_stack_size - self.stack_size
        if can_accept <= 0:
            log.debug(f"Cannot merge {other=} because {self=} is at max stack_size.")
            return other

        to_move = min(can_accept, other.stack_size)
        self.stack_size += to_move
        other.stack_size -= to_move
        if other.stack_size != 0:
            log.debug(
                f"Partially merged {other=} because {self=} is at max stack_size."
            )
            return other

        log.debug(f"Fully merged {other=} into {self=}.")
        return None
