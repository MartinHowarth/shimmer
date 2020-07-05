import pytest

from shimmer.logistics.inventory import Inventory
from shimmer.logistics.item import Item, ItemDefinition


@pytest.fixture
def dummy_inventory(dummy_item_definition, dummy_stackable_item_definition):
    return Inventory(
        items=[Item(dummy_item_definition, 1) for _ in range(3)]
        + [Item(dummy_stackable_item_definition, 20) for _ in range(3)],
        capacity=10,
    )


def test_get_item_references(subtests, dummy_item_definition, dummy_inventory):
    items = list(dummy_inventory.get_item_references(dummy_item_definition))
    assert len(items) == 3
    for item in items:
        assert item.definition == dummy_item_definition
        # Ensure the item filtered out is actually a reference to the actual item, not an
        # identical copy, which is what "x in list" would compare.
        assert any([item is orig_item for orig_item in dummy_inventory.items])


def test_contains(dummy_item_definition, dummy_inventory):
    assert dummy_item_definition in dummy_inventory
    other_definition = ItemDefinition("not_used", "Other Item")
    assert other_definition not in dummy_inventory


def test_add_item_non_stackable(
    subtests, dummy_item_definition,
):
    item_1 = Item(dummy_item_definition, 1)
    item_2 = Item(dummy_item_definition, 1)
    with subtests.test("Can add non-stackable item to inventory with space."):
        inventory = Inventory(items=[], capacity=1)
        result = inventory.add_item(item_1)
        assert result is None
        assert inventory.items == [item_1]

    with subtests.test(
        "Can add multiple non-stackable items to inventory with space if "
        "duplicates are allowed."
    ):
        capacity = 5
        inventory = Inventory(
            items=[], capacity=capacity, can_hold_duplicate_stacks=True
        )
        for i in range(capacity):
            item = Item(dummy_item_definition, 1)
            result = inventory.add_item(item)
            assert result is None
        assert len(inventory.items) == capacity
        del item

    with subtests.test(
        "Cannot add multiple non-stackable items to inventory with space if "
        "duplicates are not allowed."
    ):
        inventory = Inventory(items=[], capacity=5, can_hold_duplicate_stacks=False)
        assert inventory.add_item(item_1) is None
        assert inventory.add_item(item_2) is item_2
        assert inventory.items == [item_1]

    with subtests.test("Cannot add non-stackable item to inventory with no space."):
        inventory = Inventory(items=[], capacity=1)
        # First adds successfully
        assert inventory.add_item(item_1) is None

        # Second fails to add and is returned unchanged.
        result = inventory.add_item(item_2)
        assert result is item_2
        assert result.stack_size == 1
        assert inventory.items == [item_1]


def test_add_item_stackable(
    subtests, dummy_stackable_item_definition,
):
    max_stack_size = 50
    full_stack = Item(dummy_stackable_item_definition, max_stack_size)
    partial_stack_1 = Item(dummy_stackable_item_definition, 40)
    partial_stack_2 = Item(dummy_stackable_item_definition, 20)
    partial_stack_3 = Item(dummy_stackable_item_definition, 10)
    partial_combination_overflow_size = (
        partial_stack_1.stack_size + partial_stack_2.stack_size - max_stack_size
    )

    def reset_stacks():
        nonlocal full_stack, partial_stack_1, partial_stack_2, partial_stack_3
        full_stack = Item(dummy_stackable_item_definition, max_stack_size)
        partial_stack_1 = Item(dummy_stackable_item_definition, 40)
        partial_stack_2 = Item(dummy_stackable_item_definition, 20)
        partial_stack_3 = Item(dummy_stackable_item_definition, 10)

    with subtests.test("Can add stackable item to empty inventory."):
        inventory = Inventory(items=[], capacity=1)
        result = inventory.add_item(full_stack)
        assert result is None
        assert inventory.items == [full_stack]

    reset_stacks()
    with subtests.test(
        "Can add multiple stackable items to inventory with space if "
        "duplicates are allowed without overflow."
    ):
        capacity = 5
        inventory = Inventory(
            items=[], capacity=capacity, can_hold_duplicate_stacks=True
        )
        for i in range(capacity):
            item = Item(dummy_stackable_item_definition, max_stack_size)
            result = inventory.add_item(item)
            assert result is None
        assert len(inventory.items) == capacity
        del item

    reset_stacks()
    with subtests.test(
        "Can add partial stack to another partial stack without overflow."
    ):
        inventory = Inventory(items=[], capacity=2, can_hold_duplicate_stacks=True)
        result = inventory.add_item(partial_stack_1)
        assert result is None
        result = inventory.add_item(partial_stack_2)
        assert result is None
        assert inventory.items == [
            Item(dummy_stackable_item_definition, max_stack_size),
            Item(dummy_stackable_item_definition, partial_combination_overflow_size,),
        ]

    reset_stacks()
    with subtests.test("Can add partial stack to another partial stack with overflow."):
        inventory = Inventory(items=[], capacity=2)
        result = inventory.add_item(partial_stack_1)
        assert result is None
        result = inventory.add_item(partial_stack_3)
        assert result is None
        assert inventory.items == [
            Item(dummy_stackable_item_definition, max_stack_size)
        ]

    reset_stacks()
    with subtests.test(
        "Cannot add multiple stackable items to inventory with space if "
        "duplicates are not allowed, with no overflow."
    ):
        inventory = Inventory(items=[], capacity=5, can_hold_duplicate_stacks=False)
        assert inventory.add_item(full_stack) is None
        assert inventory.add_item(partial_stack_1) is partial_stack_1
        assert inventory.items == [full_stack]

    reset_stacks()
    with subtests.test(
        "Can add part of a stack to another partial stack with overflow and "
        "no duplicates allowed."
    ):
        inventory = Inventory(items=[], capacity=2, can_hold_duplicate_stacks=False)
        result = inventory.add_item(partial_stack_1)
        assert result is None
        result = inventory.add_item(partial_stack_2)
        assert result is partial_stack_2
        assert partial_stack_2.stack_size == partial_combination_overflow_size
        assert inventory.items == [
            Item(dummy_stackable_item_definition, max_stack_size)
        ]

    reset_stacks()
    with subtests.test("Cannot add stackable item to inventory with no space."):
        inventory = Inventory(items=[], capacity=1)
        # First adds successfully
        assert inventory.add_item(full_stack) is None

        # Second fails to add and is returned unchanged.
        result = inventory.add_item(partial_stack_1)
        assert result is partial_stack_1
        assert inventory.items == [full_stack]
