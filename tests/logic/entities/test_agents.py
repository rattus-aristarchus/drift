import copy
import dataclasses
from typing import List

import pytest

from src.logic.entities import agents
from src.logic.entities.agents import Population, Resource
from src.logic.entities.structures import Structure
from src.logic.entities.cells import Cell


def sample_effect():
    return "effect executed"


@pytest.fixture
def sample_cell():
    return Cell(0, 0)


@pytest.fixture
def sample_struct():
    return Structure(name="test_struct")


@pytest.fixture
def sample_struct_1():
    return Structure(name="test_struct_1")


def test_copy_pop_is_different(sample_cell, sample_struct, sample_struct_1):
    pop = Population(name="test_pop")
    pop.structures.append(sample_struct)
    sample_cell.pops.append(pop)

    pop.size = 5

    copy_pop = agents.copy_pop_without_owned(pop, sample_cell)
    copy_pop.structures.append(sample_struct_1)
    copy_pop.size += 1

    assert pop.size == 5
    assert len(pop.structures) == 1


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
