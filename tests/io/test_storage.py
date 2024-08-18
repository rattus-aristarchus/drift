import dataclasses
import os.path

import pytest
import yaml

from src.io import storage
from src.logic import models
from src.logic.models import ModelStorage, BiomeModel, ResourceModel, NeedModel, Model
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


@dataclasses.dataclass
class TestModel0(Model):

    yaml_tag = '!TestModel0'


@dataclasses.dataclass
class TestModel1(Model):

    yaml_tag = '!TestModel1'


def test_load_model_file():
    path = os.path.join(ENTITIES_DIR, "model_folder")
    """
    yaml.add_constructor(
        tag='!TestModel0',
        constructor=TestModel0.__init__
    )
    yaml.add_constructor(
        tag='!TestModel1',
        constructor=TestModel1.__init__
    )
    
#    yaml.add_path_resolver('!model_0', ['TestModel0'], dict)
#    yaml.add_path_resolver('!model_1', ['TestModel1'], dict)
    """

    models = storage.load_all_models(path)

    assert len(models) == 3
    assert models[0].id == "0"
    assert isinstance(models[0], TestModel0)
    assert models[1].id == "1"
    assert isinstance(models[1], TestModel1)
    assert models[2].id == "5"
    assert isinstance(models[1], TestModel1)


@dataclasses.dataclass
class TestModelWithLink(Model):

    link_field: list = models.model_list()


@dataclasses.dataclass
class TestModelLinked(Model):

    pass


def test_model_links():
    model_0 = TestModelWithLink()
    model_1 = TestModelLinked(id="test_link")
    model_0.link_field.append("test_link")
    model_list = [model_0, model_1]

    sorted_models = storage.sort_model_links(model_list)

    assert model_0.link_field[0] == model_1
