import dataclasses
import os.path

import pytest

from src.io import storage, load_factory, load_worlds
from src.logic.entities.agents.populations import Need
from src.logic.entities.cells import Biome
from src.logic.entities.factories import Factory
from src.logic.entities.grids import Grid
from src.io.models import Model
from tests.io.conftest import RESOURCES_DIR, WORLDS_DIR


@pytest.fixture
def test_factory():
    result = Factory()
    result.biomes["test_biome"] = Biome(name="test_biome")
    result.biomes["test_biome_2"] = Biome(name="test_biome_2")
    return result


def test_load_tiled_map(test_factory):
    path = os.path.join(RESOURCES_DIR, "map.csv")

    map = load_worlds._load_map_from_tiled(path, test_factory)

    assert map.cells[0][2].biome.name == "test_biome_2"


def test_load_models_has_proper_links():
    factory = storage.make_factory_from_namespace(WORLDS_DIR)

    biome_resource = factory.new_biome("test_biome").starting_resources[0][0]
    assert isinstance(biome_resource, str)
    assert biome_resource == "test_input"
    pop_production = factory.new_population("test_pop").produces[0]
    assert isinstance(pop_production, str)
    assert pop_production == "test_output"
    pop_need = factory.new_population("test_pop").needs[0]
    assert isinstance(pop_need, Need)
    assert pop_need.type == "test_food"
    resource_input = factory.new_resource("test_output").inputs[0]
    assert isinstance(resource_input, str)
    assert resource_input == "test_input"


@dataclasses.dataclass
class SampleModel0(Model):

    yaml_tag = '!SampleModel0'


@dataclasses.dataclass
class SampleModel1(Model):

    yaml_tag = '!SampleModel1'


def test_load_model_file():
    path = os.path.join(RESOURCES_DIR, "free_structure")

    models = storage._load_all_models(path)

    assert len(models) == 3
    assert models[0].name == "0"
    assert isinstance(models[0], SampleModel0)
    assert models[1].name == "1"
    assert isinstance(models[1], SampleModel1)
    assert models[2].name == "5"
    assert isinstance(models[1], SampleModel1)

"""
# under current implementation, missing fields don't have to be initialized 
def test_missing_fields_are_initialized():
    path = os.path.join(RESOURCES_DIR, "for_missing_fields")

    models = storage._load_all_models(path)

    assert models[0].type == ""
    assert len(models[0].needs) == 0
"""

def test_load_factory():
    models = storage._load_models_and_replace_effects(WORLDS_DIR)

    factory = load_factory.make_factory_from_models(models)

    assert len(factory.biomes) == 2
    assert len(factory.populations) == 1
    assert len(factory.resources) == 3


def test_load_worlds():
    models = storage._load_models_and_replace_effects(WORLDS_DIR)
    factory = load_factory.make_factory_from_models(models)
    worlds = list(factory.worlds.values())

    load_worlds.load_maps_into_worlds(worlds, WORLDS_DIR, factory)

    assert not worlds[0].map == ''
    assert isinstance(worlds[0].map, Grid)
