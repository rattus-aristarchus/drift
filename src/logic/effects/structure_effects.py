"""
Общее правило: все чтения состояния должны производиться из
состояния предшествующего хода, запись состояния делается
в текущий ход. Таким образом, последовательность выполнения
эффектов в данном ходу не влияет на результат.
"""

from random import Random

import src.logic.entities.agents.agents
from src.logic.entities.agents.structures import Market


def get_effect(func_name):
    """
    This function is injected into modules that need to use
    effect. Don't worry about it.
    """
    return eval(func_name)


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

        src.logic.entities.agents.agents.add_ownership(
            purchase.seller,
            market.product,
            round(purchase.amount / price)
        )
        src.logic.entities.agents.agents.subtract_ownership(
            purchase.seller,
            market.exchange,
            purchase.amount
        )

    src.logic.entities.agents.agents.add_ownership(
        market.sale.seller,
        market.exchange,
        round(market.sale.amount * price)
    )
    src.logic.entities.agents.agents.subtract_ownership(
        market.sale.seller,
        market.product,
        market.sale.amount
    )
