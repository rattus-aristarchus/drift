import pytest

from src.logic.entities import cells
from src.logic.entities.agents.resources import Resource
from src.logic.entities.cells import Biome
from src.logic.entities.factory import Factory


def test_resources_are_created():
    factory = Factory()
    resource = Resource(name="test_resource")
    factory.resources["test_resource"] = resource
    biome = Biome(name="test_biome")
    biome.starting_resources=[
        ("test_resource", 5)
    ]
    factory.biomes["test_biome"] = biome

    cell = cells.create_cell(0, 0, "test_biome", factory)

    assert len(cell.resources) > 0
    assert cell.resources[0].name == "test_resource"
    assert cell.resources[0].size == 5

