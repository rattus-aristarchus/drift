import random
from kivy.logger import Logger

from src.logic.entities import histories, agents
from src.logic.entities.agents import Resource


def do(world_model, model_base):
    """
    This function is called once, at the beginning, creating the history
    object with the first grid.
    :param world_model: a model from which to generate the first grid
    :param model_base: a base from which all entities in history will be generated
    :return: a history object
    """

    if world_model.map != "":
        history = histories.create_with_premade_map(world_model, model_base)
    else:
        history = histories.create_with_generated_map(world_model, model_base)

    grid = history.current_state()

    for cell_dict in world_model.cells:
        # the world model contains a list of instructions for
        # populating cells
        _do_populate_instruction(cell_dict, grid, model_base)

    return history


def _do_populate_instruction(instructions, grid, model_base):
    populated_cells = []

    if instructions['location'] == 'everywhere':
        # the instruction has to be repeated for every cell on the map
        for x, column in grid.cells.items():
            for y, cell in column.items():
                _populate_cell(cell, instructions, model_base)
                populated_cells.append(cell)

    elif instructions['location'] == 'random':
        # the instruction has to be applied to a 'repeat'
        # number of times
        if 'repeat' in instructions.keys():
            repeat = instructions['repeat']
        else:
            repeat = 1
        for i in range(repeat):
            cell = _retreive_cell(instructions, grid)
            _populate_cell(cell, instructions, model_base)
            populated_cells.append(cell)

    elif isinstance(instructions['location'], list):
        # the instruction contains coordinates of the cell
        # it has to be applied to
        x = instructions['location'][0]
        y = instructions['location'][1]
        _populate_cell(grid.cells[x][y], instructions, model_base)
        populated_cells.append(grid.cells[x][y])

    if 'watch' in instructions.keys() and instructions['watch']:
        # we write output like graphs for watched cells
        grid.watched_cells.extend(populated_cells)


def _retreive_cell(cell_dict, grid):
    if cell_dict['location'] == 'random':
        cell = _rand_cell(grid)
    else:
        loc = cell_dict['location']
        cell = grid.cells[loc[0]][loc[1]]
    return cell


def _populate_cell(cell, cell_dict, model_base):
    if 'pops' in cell_dict.keys():
        for pop_dict in cell_dict['pops']:
            pop_model = model_base.get_pop(pop_dict['name'])
            pop = agents.create_pop(pop_model, cell)
            pop.size = pop_dict['size']
            Logger.debug("Populate_cell: created pop " + pop.name +
                         " of size " + str(pop.size))

    if 'resources' in cell_dict.keys():
        for res_dict in cell_dict['resources']:
            model = model_base.get_res(res_dict['name'])
            resource = agents.create_resource(model, cell)
            resource.size = res_dict['size']
            cell.resources.append(resource)
            Logger.debug("Populate_cell: created resource " + resource.name +
                         " of size " + str(resource.size))


def _rand_cell(map):
    return map.cells[random.randint(0, map.width - 1)][random.randint(0, map.height - 1)]

