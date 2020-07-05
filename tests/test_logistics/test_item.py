import pytest

from shimmer.logistics.item import Item


def test_item_definition_is_stackable(
    subtests, dummy_item_definition, dummy_stackable_item_definition
):
    with subtests.test("Non-stackable item definition is not stackable."):
        assert dummy_item_definition.is_stackable is False
    with subtests.test("Stackable item definition is stackable."):
        assert dummy_stackable_item_definition.is_stackable is True


def test_item_post_init(subtests, dummy_item_definition):
    with subtests.test("Non-stackable item not allowed to have stack size > 1"):
        with pytest.raises(ValueError):
            _ = Item(dummy_item_definition, 20)

    with subtests.test("Non-stackable item allowed to have stack size == 1 or 0"):
        _ = Item(dummy_item_definition, 1)
        _ = Item(dummy_item_definition, 0)

    with subtests.test("Item not allowed to have negative stack size"):
        with pytest.raises(ValueError):
            _ = Item(dummy_item_definition, -1)


def test_receive_merge(
    subtests, dummy_item_definition, dummy_stackable_item_definition
):
    with subtests.test("Non-stackable item fails to merge with non-stackable item."):
        item = Item(dummy_item_definition, 1)
        item2 = Item(dummy_item_definition, 1)
        merge_result = item2.receive_merge(item)
        assert merge_result is item
        assert item.stack_size == 1
        assert item2.stack_size == 1

    with subtests.test("Items of different type fail to merge."):
        item = Item(dummy_item_definition, 1)
        item2 = Item(dummy_stackable_item_definition, 50)
        merge_result = item2.receive_merge(item)
        assert merge_result is item
        assert item.stack_size == 1
        assert item2.stack_size == 50

    with subtests.test("Stackable items can merge within max stack size."):
        item = Item(dummy_stackable_item_definition, 1)
        item2 = Item(dummy_stackable_item_definition, 40)
        merge_result = item2.receive_merge(item)
        assert merge_result is None
        assert item.stack_size == 0
        assert item2.stack_size == 41

    with subtests.test("Stackable items can merge beyond max stack size."):
        item = Item(dummy_stackable_item_definition, 10)
        item2 = Item(dummy_stackable_item_definition, 45)
        merge_result = item2.receive_merge(item)
        assert merge_result is item
        assert item.stack_size == 5
        assert item2.stack_size == 50
