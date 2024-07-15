import pytest

from src.logic.models import ModelStorage, BiomeModel


@pytest.fixture
def model_base():
    result = ModelStorage()
    biome_model = BiomeModel("test_biome")
    result.biomes.append(biome_model)
    return result
