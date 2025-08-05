import pytest
from src import effects_util
from src.logic.effects import effects
from src.logic.entities import grids
from src.logic.entities.agents.populations import Population
from src.logic.entities.cells import Biome
from src.logic.entities.factories import Factory
from src.logic.entities.histories import History, World

@pytest.fixture
def factory_with_default_biome():
    default_biome = Biome(name="default_biome")
    factory = Factory()
    factory.biomes["default_biome"] = default_biome
    return factory

@pytest.fixture
def history():
    world = World(width=5, height=5)
    output = History(world, lambda *args: None)
    return output


@pytest.fixture
def fresh_grid(history, factory_with_default_biome):
    output = grids.create_grid_with_default_biome(
        history.world.width,
        history.world.height,
        "default_biome",
        factory_with_default_biome
    )
    output.cells[0][0].pops.append(Population(name="test_pop"))
    return output
