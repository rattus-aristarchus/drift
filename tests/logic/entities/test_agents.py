import copy
import dataclasses
from typing import List
import pytest
from src.logic.effects import util
from src.logic.effects.agent_effects import social
from src.logic.entities import agents
from src.logic.entities.agents import Population, Resource, Need
from src.logic.entities.structures import Structure
from src.logic.entities.cells import Cell
from src.logic.models import NeedModel, ModelStorage


def sample_effect():
    return "effect executed"


@pytest.fixture
def sample_cell():
    return Cell(x=0, y=0)


def test_copy_pop_is_different(sample_cell):
    pop = Population(name="test_pop")
    test_need = Need(name="test_need")
    test_need_1 = Need(name="test_need_1")
    pop.needs.append(test_need)
    sample_cell.pops.append(pop)

    pop.size = 5

    copy_pop = agents.copy_pop_without_owned(pop, sample_cell)
    copy_pop.needs.append(test_need_1)
    copy_pop.size += 1

    assert pop.size == 5
    assert len(pop.needs) == 1


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
        id="test_need",
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
