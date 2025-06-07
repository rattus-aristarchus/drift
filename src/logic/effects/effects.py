"""
Это файл-диспетчер; когда логике нужно получить функцию
эффекта, зная только ее имя, она обращается сюда к функции
get_effect.
"""

from src.logic.computation import Buffer
from src.logic.effects import world_effects, cell_effects, structure_effects
from src.logic.effects.agent_effects import migration, production, consumption, social


def get_effect(func_name):
    """
    Возвращает ссылку на функцию эффекта по имени функции
    """
    return eval(func_name)


"""
Ниже - эффекты уровня клетки; у всех по три аргумента
- объект
- буфер клетки
- буфер карты
"""

"""
Эффекты популяций
"""

def migrate(pop, cell, buffer):
    migration.migrate(pop, cell)


def brownian_migration(pop, cell, buffer):
    migration.brownian_migration(pop, cell)


def producer_grow(pop, cell, buffer):
    consumption.producer_grow(pop)


def basic_agriculture(pop, cell, buffer):
    product = pop.produces[0]
    production.natural_resource_exploitation(pop, product, cell, buffer)


def produce(pop, cell, buffer):
    production.produce(pop, cell, buffer)


def do_food(pop, cell, buffer):
    consumption.do_food(pop, cell)


def social_mobility(pop, cell, buffer):
    social.social_mobility(pop, cell)


def exchange(market, cell, buffer):
    structure_effects.exchange(market)


def pop_to_market(pop, cell, buffer):
    social.sell(pop, cell)
    social.buy(pop, cell)


"""
Эффекты ресурсов
"""


def grow_natural(res, cell, buffer):
    consumption.natural_growth(res, cell)


def grow(res, cell, buffer):
    consumption.growth(res)


"""
Эффекты клеток
"""


def temp_change(cell, buffer):
    cell_effects.temp_change(cell, buffer)


"""
Ниже - эффекты уровня карты; у всех по два аргумента
- карта
- буфер
"""


def climate(grid, buffer: Buffer):
    world_effects.climate(grid, buffer)
