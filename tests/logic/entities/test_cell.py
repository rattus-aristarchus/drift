import pytest

from src.logic.entities import cells
from src.logic.entities.agents import Population
from src.logic.entities.structures import Structure
from src.logic.entities.cells import Cell, Biome
from src.logic.models import BiomeModel, ResourceModel


@pytest.fixture
def cell_with_pop():
    cell = Cell(0, 0)
    pop = Population(name="test_pop")
    cell.pops.append(pop)
    return cell


def test_resources_are_created():
    resource_model = ResourceModel(
        id="test_resource"
    )
    biome_model = BiomeModel(
        resources=[
            (resource_model, 5)
        ]
    )

    cell = cells.create_cell(0, 0, biome_model)

    assert len(cell.resources) > 0
    assert cell.resources[0].name == "test_resource"
    assert cell.resources[0].size == 5


def test_copy_cell_is_different(cell_with_pop):
    test_struct = Structure()
    test_biome = Biome()
    test_biome.capacity["test_pop"] = 1
    cell_with_pop.get_pop("test_pop").size = 5
    cell_with_pop.get_pop("test_pop").structures.append(test_struct)
    cell_with_pop.structures.append(test_struct)
    cell_with_pop.biome = test_biome

    # act
    copy = cells.copy_cell_without_structures(cell_with_pop)
    copy.structures[0].name = "old_structure"
    copy.biome.capacity["test_pop"] += 1

    # make sure originals haven't changed
    assert copy.get_pop("test_pop").size == 5
    assert len(copy.get_pop("test_pop").structures) > 0
    assert copy.structures[0] == test_struct
    assert test_biome.capacity["test_pop"] == 1
