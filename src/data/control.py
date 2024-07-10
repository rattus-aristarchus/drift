import random
from kivy.logger import Logger

import src.data.history
from src.data import cells
from src.data.effects import pop_effects, world_effects
from src.data.history import History


def generate_history(world):
    """
    This function is called once, at the beginning, creating the history
    object with the first grid.
    :param world: a dictionary with the data used to generate the first grid
    :return: a history object
    """
    history = History(world['width'], world['height'])
    if 'effects' in world.keys():
        _add_history_effects(history, world['effects'])
    grid = history.current_state()

    for number, cell_dict in world['cells'].items():
        if cell_dict['location'] == 'everywhere':
            for x, column in grid.cells.items():
                for y, cell in column.items():
                    _populate_cell(cell, cell_dict)
        else:
            if 'repeat' in cell_dict.keys():
                repeat = cell_dict['repeat']
            else:
                repeat = 1
            for i in range(repeat):
                cell = _retreive_cell(cell_dict, grid)
                _populate_cell(cell, cell_dict)
                if 'watch' in cell_dict.keys() and cell_dict['watch']:
                    grid.watched_cells.append(cell)

    return history


def _add_history_effects(history, effect_names):
    for func_name in effect_names:
        effect = src.data.history.get_world_effect(func_name)
        history.effects.append(effect)


def _retreive_cell(cell_dict, grid):
    if cell_dict['location'] == 'random':
        cell = _rand_cell(grid)
    else:
        loc = cell_dict['location']
        cell = grid.cells[loc[0]][loc[1]]
    return cell


def _populate_cell(cell, cell_dict):
    for number, pop_dict in cell_dict['pops'].items():
        pop = cells.create_pop(cell, pop_dict['name'])
        pop.size = pop_dict['size']
        Logger.debug("Control, populate_cell: created pop " + pop.name +
                     " of size " + str(pop.size))


def _rand_cell(map):
    return map.cells[random.randint(0, map.width - 1)][random.randint(0, map.height - 1)]

