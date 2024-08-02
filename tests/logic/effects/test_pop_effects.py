import pytest
from src.logic.effects import util
from src.logic.effects.pop_effects import production


def test_growth_with_capacity():
    result = util.growth_with_capacity(1000, 10000, 0.05)

    assert result == 45


test_data = [
    (50, 1, 1, 25),
    (50, 0, 1, 0),
    (50, 1, 0, 0),
    (0, 1, 1, 0)
]


@pytest.mark.parametrize("optimum,labor_per_land,land_used,expected_result", test_data)
def test_hyperbolic(optimum, labor_per_land, land_used, expected_result):
    result = production.hyperbolic_function(optimum, labor_per_land, land_used)
    assert result == expected_result
