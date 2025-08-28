import pytest

from src.logic.computation import Buffer
from src.logic.effects import effects_util
from src.logic.effects.agent_effects import consumption
from src.logic.entities.agents import ownership
from src.logic.entities.agents.populations import Need
from src.logic.entities.basic import recurrents
from src.logic.entities.cells import Cell
from src.logic.entities.worlds import World


def test_growth_with_capacity():
    result = effects_util.growth_with_capacity(1000, 10000, 0.05)

    assert result == 45

@pytest.fixture
def consumption_setup(init_factory):
    test_cell = Cell()
    test_pop = effects_util.factory.new_population("test_pop")
    test_pop.size = 1000
    test_pop.needs.append(
        Need(
            type="food",
            per_1000=1000
        )
    )
    test_cell.pops.append(test_pop)
    food = effects_util.factory.new_resource("test_crop")
    food.type = "food"
    food.size = 1500
    test_cell.resources.append(food)
    return test_cell, test_pop, food


def test_consumption_reduces_food(consumption_setup):
    test_cell, test_pop, food = consumption_setup
    ownership.set_ownership(test_pop, food, 1500)
    test_cell_write, all_recurrents = recurrents.copy_recurrent_and_add_to_list(test_cell, {})
    test_pop_write = test_cell_write.pops[0]
    test_pop_write.age = 1

    consumption.do_food(test_pop_write, test_pop, test_cell_write, test_cell)

    assert test_cell_write.resources[0].size == 500


def cant_eat_others_food(consumption_setup):
    test_cell, test_pop, food = consumption_setup
    ownership.set_ownership(test_pop, food, 500)
    test_cell_write, all_recurrents = recurrents.copy_recurrent_and_add_to_list(test_cell, {})
    test_pop_write = test_cell_write.pops[0]
    test_pop_write.age = 1

    consumption.do_food(test_pop_write, test_pop, test_cell_write, test_cell)

    assert test_cell_write.resources[0].size == 1000
