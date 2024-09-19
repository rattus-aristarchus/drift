import pytest
from src.logic.entities.agents.populations import Population


@pytest.fixture
def dic_for_object():
    dic = {
        "name": "test_object",
        "sapient": "True"
    }
    return dic


def test_to_object(dic_for_object):
    test_pop = Population(**dic_for_object)

    assert test_pop.name == "test_object"
    assert test_pop.sapient
