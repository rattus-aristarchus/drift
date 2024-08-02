import pytest

from src.logic.entities import generate_history
from src.logic.models import ModelStorage, PopModel


@pytest.fixture
def model_base():
    result = ModelStorage()
    model = PopModel(id="test_pop")
    result.pops.append(model)
    return result


def test_do_populate_instruction(fresh_grid, model_base):
    instruction = {
        "location": [0, 1],
        "pops": [
            {
                "name": "test_pop",
                "size": 1000
            }
        ]
    }

    generate_history._do_populate_instruction(instruction, fresh_grid, model_base)

    assert fresh_grid.cells[0][1].pops[0].name == "test_pop"
