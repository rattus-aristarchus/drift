import pytest

from src.logic.entities import grids
from src.logic.entities.agents import Population
from src.logic.entities.histories import History
from src.logic.models import ModelStorage, BiomeModel, WorldModel


@pytest.fixture
def model_base():
    result = ModelStorage()
    biome_model = BiomeModel("test_biome")
    result.biomes.append(biome_model)
    return result


@pytest.fixture
def history():
    wm = WorldModel(width=5, height=5)
    output = History(wm, lambda *args: None)
    return output


@pytest.fixture
def fresh_grid(history):
    output = grids.create_grid(history.world_model.width, history.world_model.height, BiomeModel())
    output.cells[0][0].pops.append(Population(name="test_pop"))
    return output
