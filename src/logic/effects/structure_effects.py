"""
Общее правило: все чтения состояния должны производиться из
состояния предшествующего хода, запись состояния делается
в текущий ход. Таким образом, последовательность выполнения
эффектов в данном ходу не влияет на результат.
"""

from random import Random

from src.logic.entities import cells


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
