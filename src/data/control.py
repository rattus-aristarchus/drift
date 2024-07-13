import random
from kivy.logger import Logger

import src.data
from src.data import agents, histories


def generate_history(world_model, model_base):
    """
    This function is called once, at the beginning, creating the history
    object with the first grid.
    :param world: a dictionary with the data used to generate the first grid
    :model base: a base from which all entities in history will be generated
    :return: a history object
    """

    history = histories.create_history(
        world_model,
        model_base,
    )

    grid = history.current_state()

    for number, cell_dict in world_model.cells.items():
        if cell_dict['location'] == 'everywhere':
            for x, column in grid.cells.items():
                for y, cell in column.items():
                    _populate_cell(cell, cell_dict, model_base)
        else:
            if 'repeat' in cell_dict.keys():
                repeat = cell_dict['repeat']
            else:
                repeat = 1
            for i in range(repeat):
                cell = _retreive_cell(cell_dict, grid)
                _populate_cell(cell, cell_dict, model_base)
                if 'watch' in cell_dict.keys() and cell_dict['watch']:
                    grid.watched_cells.append(cell)

    return history


def _retreive_cell(cell_dict, grid):
    if cell_dict['location'] == 'random':
        cell = _rand_cell(grid)
    else:
        loc = cell_dict['location']
        cell = grid.cells[loc[0]][loc[1]]
    return cell


def _populate_cell(cell, cell_dict, model_base):
    for number, pop_dict in cell_dict['pops'].items():
        pop_model = model_base.get_pop(pop_dict['name'])
        pop = agents.create_pop(pop_model, cell)
        pop.size = pop_dict['size']
        Logger.debug("Control, populate_cell: created pop " + pop.name +
                     " of size " + str(pop.size))


def _rand_cell(map):
    return map.cells[random.randint(0, map.width - 1)][random.randint(0, map.height - 1)]

