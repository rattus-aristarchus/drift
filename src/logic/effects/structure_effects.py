"""
Общее правило: все чтения состояния должны производиться из
состояния предшествующего хода, запись состояния делается
в текущий ход. Таким образом, последовательность выполнения
эффектов в данном ходу не влияет на результат.
"""

from random import Random

from src.logic.entities import cells, agents
from src.logic.entities.structures import Structure, Market


def get_effect(func_name):
    """
    This function is injected into modules that need to use
    effect. Don't worry about it.
    """
    return eval(func_name)


def settlement(structure, grid_buffer):

    # expand the borders

    """
    if len(structure.territory) == 1:
        for neighbor in cell_buffer.neighbors:
            random = Random().randrange(0, 1)
            if random > 0.25:
                cells.add_territory(neighbor, structure)
    """

    # TODO: so here we obviously need a more fundamental mechanism for
    # how the farmers would expand into more territory


def exchange(market: Market):
    # для каждого продукта существует отдельный рынок

    # подразумевается, что все покупатели приходят
    # с одним товаром - surplus
    ttl_demand = 0
    for purchase in market.purchases:
        ttl_demand += purchase.amount

    if ttl_demand <= 0 or not market.sale or market.sale.amount <= 0:
        return

    price = ttl_demand / market.sale.amount
    market.price = price

    for purchase in market.purchases:
        if purchase.amount <= 0:
            continue

        agents.add_ownership(
            purchase.seller,
            market.product,
            round(purchase.amount / price)
        )
        agents.subtract_ownership(
            purchase.seller,
            market.exchange,
            purchase.amount
        )

    agents.add_ownership(
        market.sale.seller,
        market.exchange,
        round(market.sale.amount * price)
    )
    agents.subtract_ownership(
        market.sale.seller,
        market.product,
        market.sale.amount
    )
