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
    num = util.get_res_size(res.name, cell_buffer.old_cell)
    capacity = cell_buffer.old_cell.biome.get_capacity(res.name)

    res.size += util.growth_with_capacity(num, capacity, res.yearly_growth)
