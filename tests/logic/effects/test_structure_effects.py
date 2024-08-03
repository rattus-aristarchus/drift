import pytest

from src.logic.effects import structure_effects
from src.logic.entities import agents
from src.logic.entities.agents import Resource, Population
from src.logic.entities.structures import Market, Commodity


def test_exchange_happy_path():
    seller = Population(name="seller")
    buyer_0 = Population(name="buyer_0")
    buyer_1 = Population(name="buyer_1")
    market = Market()
    market.product = Resource(
        size=100,
        name="stuff"
    )
    agents.set_ownership(seller, market.product, 100)
    market.exchange = Resource(
        size=1000,
        name="surplus"
    )
    agents.set_ownership(buyer_0, market.exchange, 500)
    agents.set_ownership(buyer_1, market.exchange, 500)
    market.sale = Commodity(
        seller=seller,
        amount=100
    )
    market.purchases.append(
        Commodity(
            seller=buyer_0,
            amount=500
        )
    )
    market.purchases.append(
        Commodity(
            seller=buyer_1,
            amount=250
        )
    )

    structure_effects.exchange(market)

    assert market.price == 7.5
    assert len(seller.owned_resources) == 1
    assert seller.owned_resources[0].name == "surplus"
    assert seller.name in market.exchange.owners.keys()
    assert market.exchange.owners[seller.name] == 750
    assert len(buyer_0.owned_resources) == 1
    assert buyer_0.owned_resources[0].name == "stuff"
    assert buyer_0.name in market.product.owners.keys()
    assert market.product.owners[buyer_0.name] == 67
    assert len(buyer_1.owned_resources) == 2
    assert buyer_1.name in market.exchange.owners.keys()
    assert market.exchange.owners[buyer_1.name] == 250
