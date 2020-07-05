import pytest

from shimmer.logistics.item import ItemDefinition


@pytest.fixture
def dummy_item_definition():
    return ItemDefinition(id="dummy_item", name="Dummy Item", max_stack_size=1,)


@pytest.fixture
def dummy_stackable_item_definition():
    return ItemDefinition(
        id="stackable_dummy_item", name="Dummy Item", max_stack_size=50,
    )
