from random import Random

from src.logic.entities import cells


def get_effect(func_name):
    return eval(func_name)


def settlement(group, cell_buffer, grid_buffer):
    # expand the borders
    if len(group.territory) == 1:
        for neighbor in cell_buffer.neighbors:
            random = Random().randrange(0, 1)
            if random > 0.25:
                cells.add_territory(neighbor, group)

    # TODO: so here we obviously need a more fundamental mechanism for
    # how the farmers would expand into more territory
