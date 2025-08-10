import pytest
from src.logic.computation import Buffer
from src.logic.effects import cell_effects
from src.logic.entities import grids
from src.logic.entities.cells import Biome
from src.logic.entities.factories import Factory
from src.logic.entities.histories import World
from src.logic.entities.basic import recurrents


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
def two_grids(factory_with_steppe_biome):
 #   grid = grids.create_grid_with_default_biome(1, 1, "steppe", factory_with_steppe_biome)
    old_grid = grids.create_grid_with_default_biome(1, 1, "steppe", factory_with_steppe_biome)
    grid, all_recurrents = recurrents.copy_recurrent_and_add_to_list(old_grid, {})
    grids.increase_age_for_everything(grid)
    return grid, old_grid


@pytest.fixture
def buffer():
    world = World()
    result = Buffer(world)
    return result


def test_temp_change(buffer, two_grids):
    grid = two_grids[0]
    cell = grid.cells[0][0]
    # cell.last_copy = two_grids[1].cells[0][0]
    grid.state.temperature = 6
    buffer.world.mean_temp = 7
    buffer.memory["temp_deviation"] = -1
    buffer.world.deviation_50 = 1

    cell_effects.temp_change(cell, cell.last_copy, buffer)

    assert cell.biome.capacity['sheep'] == 75000
    
