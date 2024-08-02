"""
Общее правило: все чтения состояния должны производиться из
состояния предшествующего хода, запись состояния делается
в текущий ход. Таким образом, последовательность выполнения
эффектов в данном ходу не влияет на результат.

All data for the functions are taken from the grid of the previous turn.
This is done in order to avoid a situation where several cells are pulled from the
new grid, and some of those cells have already had changes applied to
them, while others haven't.
"""
from src.logic.effects.pop_effects import migration, production, consumption


def get_effect(func_name):
    """
    This function is injected into modules that need to use
    effect. Don't worry about it.
    """
    return eval(func_name)


def producer_grow(pop, cell_buffer, grid_buffer):
    consumption.producer_grow(pop, cell_buffer, grid_buffer)


def producer_mig(pop, cell_buffer, grid_buffer):
    migration.producer_mig(pop, cell_buffer, grid_buffer)


def basic_agriculture(pop, cell_buffer, grid_buffer):
    product = pop.model.produces[0]
    production.natural_resource_exploitation(pop, product, cell_buffer.cell)


def produce(pop, cell_buffer, grid_buffer):
    production.produce(pop, cell_buffer.cell)


def do_food(pop, cell_buffer, grid_buffer):
    consumption.do_food(pop, cell_buffer, grid_buffer)
