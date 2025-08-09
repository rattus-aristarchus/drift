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

def migrate(pop_write, pop_read, cell_write, cell_read, buffer):
    migration.migrate(pop_write, pop_read, cell_write, cell_read)


def brownian_migration(pop_write, pop_read, cell_write, cell_read, buffer):
    migration.brownian_migration(pop_write, pop_read, cell_write, cell_read)


def producer_grow(pop_write, pop_read, cell_write, cell_read, buffer):
    consumption.producer_grow(pop_write, pop_read, cell_write, cell_read)


def basic_agriculture(pop_write, pop_read, cell_write, cell_read, buffer):
    product = pop_read.produces[0]
    production.production_from_resource(pop_write, pop_read, cell_write, cell_read, product, buffer)


def produce(pop_write, pop_read, cell_write, cell_read, buffer):
    production.produce(pop_write, pop_read, cell_write, cell_read, buffer)


def do_food(pop_write, pop_read, cell_write, cell_read, buffer):
    consumption.do_food(pop_write, pop_read, cell_write, cell_read)


def social_mobility(pop_write, pop_read, cell_write, cell_read, buffer):
    social.social_mobility(pop_write, pop_read, cell_write, cell_read)


def exchange(market, nothing, cell_write, cell_read, buffer):
    structure_effects.exchange(market)


def pop_to_market(pop_write, pop_read, cell_write, cell_read, buffer):
    social.sell(pop_write, pop_read, cell_write, cell_read)
    social.buy(pop_write, pop_read, cell_write, cell_read)


"""
Эффекты ресурсов
"""


def grow_natural(res_write, res_read, cell_write, cell_read, buffer):
    consumption.natural_growth(res_write, res_read, cell_write, cell_read)


def grow(res_write, res_read, cell_write, cell_read, buffer):
    consumption.growth(res_write, res_read)


"""
Эффекты клеток
"""


def temp_change(cell_write, cell_read, buffer):
    cell_effects.temp_change(cell_write, cell_read, buffer)


"""
Ниже - эффекты уровня карты; у всех по два аргумента
- карта
- буфер
"""


def climate(grid_write, grid_read, buffer: Buffer):
    world_effects.climate(grid_write, grid_read, buffer)
