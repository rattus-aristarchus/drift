import pytest

from src.logic.computation import Buffer
from src.logic.entities.basic import recurrents
from src.logic import logic_util
from src.logic.effects import effects_util
from src.logic.effects.agent_effects import production
from src.logic.entities.agents.populations import Population
from src.logic.entities.agents.resources import Resource
from src.logic.entities.cells import Cell
from src.logic.entities.histories import World


def test_growth_with_capacity():
    result = effects_util.growth_with_capacity(1000, 10000, 0.05)

    assert result == 45


test_data = [
    (50, 1, 1, 25),
    (50, 0, 1, 0),
    (50, 1, 0, 0),
    (0, 1, 1, 0)
]


@pytest.mark.parametrize("optimum,labor_per_land,land_used,expected_result", test_data)
def test_hyperbolic(optimum, labor_per_land, land_used, expected_result):
    result = production._hyperbolic_function(optimum, labor_per_land, land_used)
    assert result == expected_result


def test_tech_factor_additive():
    pop = Population(size=1000)
    tool_0 = Resource(
        name="tool",
        type="tools",
        productivity=2,
        size=500
    )
    tool_1 = Resource(
        name="tool",
        type="tools",
        productivity=2,
        size=500
    )
    pop.owned_resources.append(tool_0)
    pop.owned_resources.append(tool_1)
    pop_1 = Population(size=1000)
    tool_2 = Resource(
        name="tool",
        type="tools",
        productivity=2,
        size=1000
    )
    pop_1.owned_resources.append(tool_2)

    tech_factor = production._get_tech_factor(pop)
    tech_factor_1 = production._get_tech_factor(pop_1)

    assert tech_factor == 2
    assert tech_factor == tech_factor_1


def test_zero_productivity_production():
    pop_read = Population(size=1000)
    tool = Resource(
        name="test_tool",
        type="tool",
        productivity=1,
        size=1000
    )
    pop_read.owned_resources.append(tool)
    cell_read = Cell()
    cell_read.pops.append(pop_read)
    land = Resource(
        name="test_land",
        type="land",
        productivity=0,
        size=1000
    )
    cell_read.resources.append(land)
    prototype = Resource(
        name="test_crop",
        type="food",
        inputs=["test_land"]
    )
    world = World()
    world.deviation_50 = 1
    buffer = Buffer(world=world)
    buffer.memory["temp_deviation"] = 0
    cell_write = logic_util.copy_dataclass_with_collections(cell_read)
    pop_write = logic_util.copy_dataclass_with_collections(pop_read)

    production.production_from_resource(pop_write, pop_read, cell_write, cell_read, prototype, buffer)

    crop = cell_write.get_res("test_res")
    assert crop is not None
    assert crop.size == 0

