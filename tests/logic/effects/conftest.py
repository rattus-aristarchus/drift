import pytest

import src
from src.logic.effects import util
from src.logic.entities.agents.resources import Resource
from src.logic.entities.agents.structures import Market
from src.logic.entities.factories import Factory


@pytest.fixture
def init_factory():
    util.factory = Factory()
    util.factory.misc["market"] = Market(
        name="market",
        effects=src.logic.effects.effects.exchange
    )
    util.factory.resources["test_res"] = Resource(name="test_res")

    yield

    util.factory = None
