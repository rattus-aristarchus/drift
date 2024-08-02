import os.path

import pytest

from src.io import storage
from src.logic.models import ModelStorage, BiomeModel, ResourceModel, NeedModel
from tests.io.conftest import RESOURCES_DIR, ENTITIES_DIR, WORLDS_DIR, MAPS_DIR


@pytest.fixture
def model_base():
    result = ModelStorage()
    result.biomes.append(BiomeModel("test_biome"))
    result.biomes.append(BiomeModel("test_biome_2"))
    return result


def test_load_tiled_map(model_base):
    path = os.path.join(RESOURCES_DIR, "map.csv")

    map = storage._load_map_from_tiled(path, model_base)

    assert map.cell_matrix[0][2].biome.id == "test_biome_2"


def test_load_models_has_proper_links():
    model_storage = storage.load_models(ENTITIES_DIR, WORLDS_DIR, MAPS_DIR)

    biome_resource = model_storage.get_biome("test_biome").resources[0][0]
    assert isinstance(biome_resource, ResourceModel)
    assert biome_resource.id == "test_input"
    pop_production = model_storage.get_pop("test_pop").produces[0]
    assert isinstance(pop_production, ResourceModel)
    assert pop_production.id == "test_output"
    pop_need = model_storage.get_pop("test_pop").needs[0]
    assert isinstance(pop_need, NeedModel)
    assert pop_need.type == "test_food"
    resource_input = model_storage.get_res("test_output").inputs[0]
    assert isinstance(resource_input, ResourceModel)
    assert resource_input.id == "test_input"
