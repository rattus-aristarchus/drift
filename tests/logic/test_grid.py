import ast

import pytest

from src.logic.entities import grids
from src.logic.entities.agents import Population
from src.logic.entities.cells import Biome
from src.logic.entities.histories import History
from src.logic.models import BiomeModel


@pytest.fixture
def history():
    output = History(5, 5)
    return output


@pytest.fixture
def fresh_grid(history):
    output = grids.create_grid(history.width, history.height, BiomeModel())
    output.cells[0][0].pops.append(Population(name="test_pop"))
    return output


def test_increase_grid_age(fresh_grid):
    grids.increase_age(fresh_grid, 2)

    assert fresh_grid.cells[0][0].pops[0].age == 2


@pytest.fixture
def cell_representation():
    return '{"biome": "test_biome"}'


def test_create_cell_from_dict(cell_representation, model_base):
    cell_dict = ast.literal_eval(cell_representation)
    cell = grids.create_cell_from_dict(0, 0, cell_dict, model_base)

    assert cell.biome.model.id == "test_biome"
