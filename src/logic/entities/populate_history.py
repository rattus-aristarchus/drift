import random
from kivy.logger import Logger
from src.logic.entities import histories
from src.logic.entities.agents import populations, resources
from src.logic.entities.factories import Factory
from src.logic.entities.histories import World


def do(world: World, factory: Factory, write_output):
    """
    This function is called once, at the beginning, creating the history
    object with the first grid.
    :param world: a world from which to generate the first grid
    :param factory: a base from which all entities in history will be generated
    :return: a history object
    :param write_output: a callback to write a grid to disk
    """

    if world.map != "":
        history = histories.create_with_premade_map(world, write_output)
    else:
        history = histories.create_with_generated_map(world, factory, write_output)

    grid = history.current_state()

    for cell_dict in world.cell_instructions:
        # the world model contains a list of instructions for
        # populating cells
        _do_populate_instruction(cell_dict, grid, factory)

    return history


def _do_populate_instruction(instructions, grid, factory):
    populated_cells = []

    if instructions['location'] == 'everywhere':
        # the instruction has to be repeated for every cell on the map
        for x, column in grid.cells.items():
            for y, cell in column.items():
                _populate_cell(cell, instructions, factory)
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
            _populate_cell(cell, instructions, factory)
            populated_cells.append(cell)

    elif isinstance(instructions['location'], list):
        # the instruction contains coordinates of the cell
        # it has to be applied to
        x = instructions['location'][0]
        y = instructions['location'][1]
        _populate_cell(grid.cells[x][y], instructions, factory)
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


def _populate_cell(cell, cell_dict, factory):
    if 'pops' in cell_dict.keys():
        for pop_dict in cell_dict['pops']:
            pop = factory.new_population(pop_dict['name'])
            cell.pops.append(pop)
            pop.size = pop_dict['size']
            Logger.debug(f"{__name__}: created pop " + pop.name +
                         " of size " + str(pop.size))

    if 'resources' in cell_dict.keys():
        for res_dict in cell_dict['resources']:
            resource = factory.new_resource(res_dict['name'])
            cell.resources.append(resource)
            resource.size = res_dict['size']
            Logger.debug(f"{__name__}: created resource {resource.name}" +
                         f" of size {str(resource.size)}")


def _rand_cell(map):
    return map.cells[random.randint(0, map.width - 1)][random.randint(0, map.height - 1)]

