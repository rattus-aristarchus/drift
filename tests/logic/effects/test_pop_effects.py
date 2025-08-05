import pytest
from src.logic.effects import effects_util
from src.logic.effects.agent_effects import production
from src.logic.entities.agents.populations import Population
from src.logic.entities.agents.resources import Resource


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
