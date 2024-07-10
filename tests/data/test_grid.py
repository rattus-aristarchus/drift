import pytest

from src.data import grid
from src.data.base_types import Population
from src.data.grid import Grid
from src.data.history import History


@pytest.fixture
def history():
    output = History(5, 5)
    return output


@pytest.fixture
def fresh_grid(history):
    output = Grid(history.width, history.height, history)
    grid.populate(output)
    output.cells[0][0].pops.append(Population("test_pop"))
    return output


def test_increase_grid_age(fresh_grid):
    grid.increase_age(fresh_grid, 2)

    assert fresh_grid.cells[0][0].pops[0].age == 2
