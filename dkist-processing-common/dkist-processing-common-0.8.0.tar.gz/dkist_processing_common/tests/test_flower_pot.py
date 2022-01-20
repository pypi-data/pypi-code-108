from typing import Any
from typing import Hashable

import pytest

from dkist_processing_common.models.flower_pot import FlowerPot
from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem


@pytest.fixture()
def simple_flower():
    class Flower(Stem):
        def setter(self, value: Any) -> Any:
            if value < 0:
                return SpilledDirt
            return value % 2

        def getter(self, key: Hashable) -> Hashable:
            return self.key_to_petal_dict[key]

    return Flower(stem_name="simple_flower")


@pytest.fixture()
def simple_flower_pot(simple_flower):
    flower_pot = FlowerPot()
    flower_pot.flowers += [simple_flower]

    return flower_pot


@pytest.fixture()
def simple_key_values():
    return {f"thing{i}": i for i in range(5)}


def test_simple_flower_pot(simple_flower_pot, simple_key_values):
    """
    Given: A FlowerPot with a simple Flower
    When: Updating rock and flower with key: value pairs
    Then: The rock and flower are correctly updated
    """
    assert len(simple_flower_pot) == 1

    flower = simple_flower_pot[0]
    assert flower.stem_name == "simple_flower"

    for k, m in simple_key_values.items():
        simple_flower_pot.add_dirt(k, m)

    petals = sorted(list(flower.petals), key=lambda x: x.value)
    assert len(petals) == 2
    assert petals[0].value == 0
    assert petals[0].keys == ["thing0", "thing2", "thing4"]
    assert petals[1].value == 1
    assert petals[1].keys == ["thing1", "thing3"]


def test_spilled_dirt_flower(simple_flower):
    """
    Given: A simple Flower with logic to deal with SpilledDirt
    When: Updating the flower with a key/value that causes dirt to be spilled
    Then: The Flower ignores the input key/value
    """
    key = "thing0"
    value = -1
    simple_flower.update(key, value)
    assert len(list(simple_flower.petals)) == 0


def test_unhashable_dirt(simple_flower_pot):
    """
    Given: A FlowerPot
    When: Adding dirt with a key that is not hashable
    Then: An Error is raised
    """
    unhashable_key = ["a", "list"]
    value = "never gonna get here"
    with pytest.raises(TypeError):
        simple_flower_pot.add_dirt(unhashable_key, value)
