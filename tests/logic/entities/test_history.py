import pytest

from src.logic.entities import populate_history
from src.logic.entities.agents.populations import Population
from src.logic.entities.factory import Factory


@pytest.fixture
def factory_with_test_pop():
    result = Factory()
    pop = Population(name="test_pop")
    result.populations.append(pop)
    return result


def test_do_populate_instruction(fresh_grid, factory_with_test_pop):
    instruction = {
        "location": [0, 1],
        "pops": [
            {
                "name": "test_pop",
                "size": 1000
            }
        ]
    }

    populate_history._do_populate_instruction(instruction, fresh_grid, factory_with_test_pop)

    assert fresh_grid.cells[0][1].pops[0].name == "test_pop"
