import logging
from dataclasses import dataclass
from typing import Optional, List, Iterable

from .item import Item, ItemDefinition

log = logging.getLogger(__name__)


@dataclass
class Inventory:
    items: List[Item]
    capacity: int
    can_hold_duplicate_stacks: bool = True

    def __contains__(self, item_definition: ItemDefinition) -> bool:
        possible_item = next(self.get_item_references(item_definition), None)
        return possible_item is not None

    def get_item_references(self, item_definition: ItemDefinition) -> Iterable[Item]:
        def type_matches(item: Item) -> bool:
            nonlocal item_definition
            return item.definition == item_definition

        return filter(type_matches, self.items)

    def add_item(self, item: Item) -> Optional[Item]:
        """
        Add an item to the inventory.

        :param item: The item to add.
        :return: None if the item (stack) was fully added to the inventory. Otherwise return
            the same item object back but with `stack_size` reduced by as many items as would
            fit into the inventory.
        """
        if item.definition in self:
            if item.definition.is_stackable:
                possible_merge_targets = self.get_item_references(item.definition)
                for merge_target in possible_merge_targets:
                    item = merge_target.receive_merge(item)
                    if item is None:
                        log.debug(f"Fully merged {item=} into existing items stacks.")
                        return None

            if not self.can_hold_duplicate_stacks:
                log.debug(
                    f"Duplicate stacks not allowed, and existing stacks full for {item=}"
                )
                return item

        # Still some (or all) of the item left to add to inventory after filling up existing
        # item stacks - try and add it as a new stack.
        if len(self.items) >= self.capacity:
            log.debug(f"Inventory full and all existing stacks full for {item=}")
            return item

        self.items.append(item)
        return None
