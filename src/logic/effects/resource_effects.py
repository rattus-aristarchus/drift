"""
Общее правило: все чтения состояния должны производиться из
состояния предшествующего хода, запись состояния делается
в текущий ход. Таким образом, последовательность выполнения
эффектов в данном ходу не влияет на результат.
"""
from src.logic.effects import util


def get_effect(func_name):
    """
    This function is injected into modules that need to use
    effect. Don't worry about it.
    """
    return eval(func_name)


def default_grow(res, cell_buffer, grid_buffer):
    num = res.last_copy.size
    capacity = cell_buffer.cell.last_copy.biome.get_capacity(res.name)

    res.size += util.growth_with_capacity(num, capacity, res.yearly_growth)
