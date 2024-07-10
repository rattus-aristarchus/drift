import random
from kivy.logger import Logger

import src.data.effects as effects
from src.data.effects import CellBuffer, GridBuffer
from src.data.history import History


def generate_history(world):
    """
    This function is called once, at the beginning, creating the history
    object with the first grid.
    :param world: a dictionary with the data used to generate the first grid
    :return: a history object
    """
    history = History(world['width'], world['height'])
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


def _retreive_cell(cell_dict, grid):
    if cell_dict['location'] == 'random':
        cell = _rand_cell(grid)
    else:
        loc = cell_dict['location']
        cell = grid.cells[loc[0]][loc[1]]
    return cell


def _populate_cell(cell, cell_dict):
    for number, pop_dict in cell_dict['pops'].items():
        pop = cell.create_pop(pop_dict['name'])
        pop.size = pop_dict['size']
        Logger.debug("Control, populate_cell: created pop " + pop.name +
                     " of size " + str(pop.size))


def _rand_cell(map):
    return map.cells[random.randint(0, map.width - 1)][random.randint(0, map.height - 1)]


def do_turn(history):
    """
    Executes one turn by creating a new grid object and adding it to the
    list of grids for past turns.
    :param history: the history object
    """
    Logger.info("Grid: doing turn")

    old_grid = history.current_state()
    new_grid = history.new_turn()

    # the gridbuffer and cellbuffers help avoid doing some
    # calculations multiple times
    grid_buffer = GridBuffer(new_grid, old_grid)
    for cell in new_grid.cells_as_list():
        cell_buffer = CellBuffer(cell, grid_buffer)

        # this is the main call that calls do_effects for all agents in a cell
        cell.do_effects(cell_buffer, grid_buffer)

        # remove pops that have died out
        to_remove = []
        for pop in cell.pops:
            if pop.size <= 0:
                to_remove.append(pop)
        for pop in to_remove:
            cell.pops.remove(pop)

    # this is bad
    for cell in new_grid.watched_cells:
        new_grid.output.write_cell(cell)
    new_grid.output.write_end_of_turn()
