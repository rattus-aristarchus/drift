import pytest
from src.logic.buffers import GridBuffer
from src.logic.effects.cell_effects import temp_change
from src.logic.entities import grids
from src.logic.entities.cells import Biome
from src.logic.entities.factories import Factory
from src.logic.entities.histories import History, World


@pytest.fixture(scope="session")
def factory_with_steppe_biome():
    factory = Factory()
    result = Biome(
        name="steppe",
        moisture="dry",
        capacity={
            "sheep": 50000
        }
    )
    factory.biomes["steppe"] = result
    return factory


@pytest.fixture
def grid_buffer(factory_with_steppe_biome):
    grid = grids.create_grid_with_default_biome(1, 1, "steppe", factory_with_steppe_biome)
    old_grid = grids.create_grid_with_default_biome(1, 1, "steppe", factory_with_steppe_biome)

    world = World()
    history = History(world)

    result = GridBuffer(grid, old_grid, history)
    return result


def test_temp_change(grid_buffer):
    cell = grid_buffer.grid.cells[0][0]
    grid_buffer.grid.state.temperature = 6
    grid_buffer.history.world.mean_temp = 7
    grid_buffer.temp_deviation = -1
    grid_buffer.history.world.deviation_50 = 1


    temp_change(cell, grid_buffer=grid_buffer)

    assert cell.biome.capacity['sheep'] == 75000
