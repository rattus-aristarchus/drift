from src.logic.entities.agents import structures, populations
from src.logic.effects import util
from src.logic.entities.agents.structures import Commodity


def social_mobility(pop, cell):
    if cell.has_res_type("ore") and cell.get_pop("blacksmiths") is None:
        blacksmiths = util.factory.new_population("blacksmiths")
        cell.pops.append(blacksmiths)
        blacksmiths.size = 1000
        pop.size -= 1000


def buy(pop, cell):
    old_pop = pop.last_copy

    for need in old_pop.needs:
        if need.actual < need.per_1000:
            surplus, amount = available_surplus(pop)
            if surplus and amount > 0:
                if need.resource:
                    market = get_market(need.resource.name, cell)
                else:
                    market = get_or_create_market_by_type(need.type, cell)
                if market:
                    market.exchange = surplus
                    market.purchases.append(
                        Commodity(pop, amount)
                    )


def sell(pop, cell):
    for resource in pop.owned_resources:
        if resource.name in pop.sells:
            how_much = resource.owners[pop.name]
            market = get_or_create_market(resource, cell)
            market.sale = Commodity(pop, how_much)


def get_market_for_type(resource_type, cell):
    market = None
    for check_market in cell.markets:
        if check_market.product.type == resource_type:
            market = check_market
    return market


def get_market(resource_name, cell):
    market = None
    for check_market in cell.markets:
        if check_market.product.name == resource_name:
            market = check_market
    return market


# TODO: возможно, это проблема. рынок добавляется в список рынков текущей клетки -
# то время как выполняются эффекты этой клетки
def get_or_create_market(resource, cell):
    market = None
    for check_market in cell.markets:
        if check_market.product == resource:
            market = check_market
        elif check_market.product is None and check_market.type == resource.type:
            market = check_market
            market.product = resource
    if not market:
        market = util.factory.new_misc("market")
        cell.markets.append(market)
        market.type = resource.type
        market.product = resource
    return market


def get_or_create_market_by_type(type, cell):
    market = None
    for check_market in cell.markets:
        if check_market.type == type and check_market.product is None:
            market = check_market
    if not market:
        market = util.factory.new_misc("market")
        cell.markets.append(market)
        market.type = type
    return market


def available_surplus(pop):
    for resource in pop.owned_resources:
        if resource.name == "surplus":
            size = resource.owners[pop.name]
            return resource, size
    return None, 0
