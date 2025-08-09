import pytest

import src
from src.logic.effects import effects_util, effects
from src.logic.entities.agents.populations import Population
from src.logic.entities.agents.resources import Resource
from src.logic.entities.agents.structures import Market
from src.logic.entities.factories import Factory


@pytest.fixture
def init_factory():
    effects_util.factory = Factory()
    effects_util.factory.misc["market"] = Market(
        name="market",
        effects=[effects.exchange]
    )
    effects_util.factory.resources["test_res"] = Resource(name="test_res")
    effects_util.factory.populations["test_pop"] = Population(name="test_pop")
    effects_util.factory.populations["test_pop"] = Resource(name="test_crop")

    yield

    effects_util.factory = None
