import pytest

from src.logic.buffers import CellBuffer, GridBuffer
from src.logic.effects.cell_effects import temp_change
from src.logic.entities import cells, grids, histories
from src.logic.entities.histories import History
from src.logic.models import BiomeModel, WorldModel


@pytest.fixture(scope="session")
def steppe_model():
    result = BiomeModel(
        id="steppe",
        moisture="dry",
        capacity={
            "sheep": 50000
        }
    )
    return result


@pytest.fixture
def grid_buffer(steppe_model):
    grid = grids.create_grid(1, 1, steppe_model)

    old_grid = grids.create_grid(1, 1, steppe_model)

    world_model = WorldModel()
    history = History(world_model)

    result = GridBuffer(grid, old_grid, history)
    return result


def test_temp_change(grid_buffer):
    cell_buffer = CellBuffer(None)
    cell = grid_buffer.grid.cells[0][0]
    grid_buffer.grid.state.temperature = 6
    grid_buffer.history.world_model.mean_temp = 7
    grid_buffer.temp_deviation = -1
    grid_buffer.history.world_model.deviation_50 = 1


    temp_change(cell, cell_buffer=cell_buffer, grid_buffer=grid_buffer)

    assert cell.biome.capacity['sheep'] == 75000
