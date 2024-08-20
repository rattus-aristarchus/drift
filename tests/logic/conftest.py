import pytest

from src.logic.effects import effects, util
from src.logic.entities import grids
from src.logic.entities.agents.populations import Population
from src.logic.entities.histories import History
from src.logic.models.models import BiomeModel, WorldModel, StructureModel
from src.logic.models.model_base import ModelBase

@pytest.fixture(scope="session")
def model_base():
    result = ModelBase()
    biome_model = BiomeModel("test_biome")
    result.biomes.append(biome_model)
    market_model = StructureModel("market")
    market_model.effects.append(effects.exchange)
    result.structures.append(market_model)
    util.model_base = result
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
