import copy
import dataclasses
from typing import List

import pytest

from src.logic.entities import agents
from src.logic.entities.agents import Population
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
