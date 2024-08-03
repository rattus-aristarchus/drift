"""
Это файл-диспетчер; когда логике нужно получить функцию
эффекта, зная только ее имя, она обращается сюда к функции
get_effect.
"""
from src.logic.buffers import GridBuffer
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


def producer_grow(pop, cell_buffer, grid_buffer):
    consumption.producer_grow(pop, cell_buffer, grid_buffer)


def producer_mig(pop, cell_buffer, grid_buffer):
    migration.producer_mig(pop, cell_buffer, grid_buffer)


def basic_agriculture(pop, cell_buffer, grid_buffer):
    product = pop.model.produces[0]
    production.natural_resource_exploitation(pop, product, cell_buffer.cell)


def produce(pop, cell_buffer, grid_buffer):
    production.produce(pop, cell_buffer.cell, grid_buffer)


def do_food(pop, cell_buffer, grid_buffer):
    consumption.do_food(pop, cell_buffer, grid_buffer)


def social_mobility(pop, cell_buffer, grid_buffer):
    social.social_mobility(pop, cell_buffer.cell)


def exchange(market, cell_buffer, grid_buffer):
    structure_effects.exchange(market)


def pop_to_market(pop, cell_buffer, grid_buffer):
    social.sell(pop, cell_buffer.cell)
    social.buy(pop, cell_buffer.cell)

"""
Эффекты ресурсов
"""


def grow_natural(res, cell_buffer, grid_buffer):
    consumption.natural_growth(res, cell_buffer.cell)


def grow(res, cell_buffer, grid_buffer):
    consumption.growth(res)


"""
Эффекты клеток
"""


def temp_change(cell, cell_buffer, grid_buffer):
    cell_effects.temp_change(cell, grid_buffer)


"""
Ниже - эффекты уровня карты; у всех по два аргумента
- объект
- буфер карты
"""


def settlement(structure, grid_buffer):
    structure_effects.settlement(structure, grid_buffer)


def climate(history, grid_buffer: GridBuffer):
    world_effects.climate(history, grid_buffer)
