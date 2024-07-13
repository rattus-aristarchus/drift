import pytest

from src.data import grids
from src.data.agents import Population
from src.data.cells import Biome
from src.data.grids import Grid
from src.data.histories import History
from src.data.models import BiomeModel


@pytest.fixture
def history():
    output = History(5, 5)
    return output


@pytest.fixture
def fresh_grid(history):
    output = grids.create_grid(history.width, history.height, Biome(BiomeModel()))
    output.cells[0][0].pops.append(Population("test_pop"))
    return output


def test_increase_grid_age(fresh_grid):
    grids.increase_age(fresh_grid, 2)

    assert fresh_grid.cells[0][0].pops[0].age == 2
