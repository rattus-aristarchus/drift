import os.path

import pytest

from src.io import storage
from src.logic.models import ModelStorage, BiomeModel
from tests.conftest import RESOURCES_DIR


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
