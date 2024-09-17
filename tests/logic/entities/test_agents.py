import dataclasses

import pytest

from src.logic.effects.agent_effects import social
from src.logic.entities.agents import agents
from src.logic.entities.agents.populations import Population, Need
from src.logic.entities.agents.resources import Resource
from src.logic.entities.basic import entities
from src.logic.entities.basic.entities import Entity
from src.logic.entities.cells import Cell
from src.logic.models.models import NeedModel


def sample_effect():
    return "effect executed"


owned_vs_free = [
    (100, 0),
    (100.1, 0),
    (-1, 100)
]


@pytest.mark.parametrize("owned,free", owned_vs_free)
def test_resource_get_free_amount_corner_cases(owned, free):
    res = Resource(
        size=100
    )
    res.owners["test_owner"] = owned

    assert res.get_free_amount() == free


def test_set_ownership_to_zero():
    pop = Population(
        name="test_pop"
    )
    res = Resource()
    pop.owned_resources.append(res)
    res.owners[pop.name] = 100

    agents.set_ownership(pop, res, 0)

    assert len(pop.owned_resources) == 0
    assert len(res.owners) == 0


def test_set_ownership_to_full():
    pop = Population(
        name="test_pop"
    )
    res = Resource(
        size=100
    )

    agents.set_ownership(pop, res)

    assert len(pop.owned_resources) == 1
    assert len(res.owners) == 1
    assert pop.name in res.owners.keys()
    assert res.owners["test_pop"] == 100


def test_buy_happy_path(model_base):
    buyer = Population()
    old_buyer = Population()
    buyer.last_copy = old_buyer
    need_model = NeedModel(
        name="test_need",
        type="test_commodity"
    )
    need = Need(
        per_1000=1000,
        actual=500
    )
    need.model = need_model
    old_buyer.needs.append(
        need
    )
    surplus = Resource(
        name="surplus",
        size=500
    )
    agents.set_ownership(buyer, surplus)
    cell = Cell()

    social.buy(buyer, cell)

    assert len(cell.markets) == 1
    assert cell.markets[0].exchange is not None
    assert len(cell.markets[0].purchases) == 1
    assert cell.markets[0].purchases[0].amount == 500

@dataclasses.dataclass
class TestSubEntity(Entity):
    pass

@dataclasses.dataclass
class TestEntity:

    sub_entity: TestSubEntity = None
    sub_entity_list: list = dataclasses.field(default_factory=lambda: [])


def test_deep_copy_entity_copies_sub_entity():
    test = TestEntity()
    sub = TestSubEntity()
    sub_1 = TestSubEntity()
    test.sub_entity = sub
    test.sub_entity_list.append(sub_1)

    copy = entities.deep_copy_simple(test)
    sub.name = "changed"
    sub_1.name = "changed"

    assert copy.sub_entity
    assert isinstance(copy.sub_entity, TestSubEntity)
    assert copy.sub_entity.name == ""
    assert len(copy.sub_entity_list) == 1
    assert isinstance(copy.sub_entity_list[0], TestSubEntity)
    assert copy.sub_entity_list[0].name == ""
