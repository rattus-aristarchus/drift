import src.logic.entities.agents.agents
from src.logic.effects import structure_effects, util
from src.logic.effects.agent_effects import social
from src.logic.entities.agents import agents
from src.logic.entities.agents.resources import Resource
from src.logic.entities.agents.populations import Population, Need
from src.logic.entities.agents.structures import Market, Commodity, Structure
from src.logic.entities.cells import Cell
from src.logic.entities.factory import Factory


def test_exchange_happy_path():
    seller = Population(name="seller")
    buyer_0 = Population(name="buyer_0")
    buyer_1 = Population(name="buyer_1")
    market = Market()
    market.product = Resource(
        size=100,
        name="stuff"
    )
    src.logic.entities.agents.agents.set_ownership(seller, market.product, 100)
    market.exchange = Resource(
        size=1000,
        name="surplus"
    )
    src.logic.entities.agents.agents.set_ownership(buyer_0, market.exchange, 500)
    src.logic.entities.agents.agents.set_ownership(buyer_1, market.exchange, 500)
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


def test_buy_happy_path():
    buyer = Population()
    old_buyer = Population()
    buyer.last_copy = old_buyer
    need = Need(
        name="test_need",
        type="test_commodity",
        per_1000=1000,
        actual=500
    )
    old_buyer.needs.append(
        need
    )
    surplus = Resource(
        name="surplus",
        size=500
    )
    agents.set_ownership(buyer, surplus)
    cell = Cell()
    util.factory = Factory()
    util.factory.structures.append(
        Market(
            name="market",
            effects=src.logic.effects.effects.exchange
        )
    )

    social.buy(buyer, cell)

    assert len(cell.markets) == 1
    assert cell.markets[0].exchange is not None
    assert len(cell.markets[0].purchases) == 1
    assert cell.markets[0].purchases[0].amount == 500
