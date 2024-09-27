import pytest

import src
from src.logic.effects import util, effects
from src.logic.entities.agents.populations import Population
from src.logic.entities.agents.resources import Resource
from src.logic.entities.agents.structures import Market
from src.logic.entities.factories import Factory


@pytest.fixture
def init_factory():
    util.factory = Factory()
    util.factory.misc["market"] = Market(
        name="market",
        effects=[effects.exchange]
    )
    util.factory.resources["test_res"] = Resource(name="test_res")
    util.factory.populations["test_pop"] = Population(name="test_pop")

    yield

    util.factory = None
