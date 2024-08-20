import pytest

from src.logic.entities import cells
from src.logic.models.models import BiomeModel, ResourceModel


@pytest.fixture
def cell_with_pop():

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

