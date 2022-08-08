import random
from kivy.logger import Logger

from data.effects import EFFECTS, CellBuffer, GridBuffer
from data.base_types import Grid, Population
from storage import Output


def generate_grid(world):
    grid = Grid(world['width'], world['height'])

    for number, cell_dict in world['cells'].items():
        if cell_dict['location'] == 'everywhere':
            for x, column in grid.cells.items():
                for y, cell in column.items():
                    populate_cell(cell, cell_dict)
        else:
            if 'repeat' in cell_dict.keys():
                repeat = cell_dict['repeat']
            else:
                repeat = 1
            for i in range(repeat):
                cell = retreive_cell(cell_dict, grid)
                populate_cell(cell, cell_dict)
                if 'watch' in cell_dict.keys() and cell_dict['watch']:
                    grid.watched_cells.append(cell)

    return grid


def retreive_cell(cell_dict, grid):
    if cell_dict['location'] == 'random':
        cell = rand_cell(grid)
    else:
        loc = cell_dict['location']
        cell = grid.cells[loc[0]][loc[1]]
    return cell


def populate_cell(cell, cell_dict):
    for number, pop_dict in cell_dict['pops'].items():
        pop = init_pop(pop_dict['name'])
        pop.size = pop_dict['size']
        cell.pops.append(pop)
        Logger.debug("Control, populate_cell: created pop " + pop.name +
                     " of size " + str(pop.size))


def rand_cell(map):
    return map.cells[random.randint(0, map.width - 1)][random.randint(0, map.height - 1)]


def do_turn(old_grid):
    Logger.info("Grid: doing turn")
    new_grid = copy_grid(old_grid)
    grid_buffer = GridBuffer(new_grid, old_grid)
    for cell in new_grid.cells_as_list():
        cell_buffer = CellBuffer(cell, grid_buffer)
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
    return new_grid


def copy_grid(old_grid):
    new_grid = Grid(old_grid.width, old_grid.height)

    for x in range(0, old_grid.width):
        for y in range(0, old_grid.height):
            old_cell = old_grid.cells[x][y]
            new_cell = new_grid.cells[x][y]
            for pop in old_cell.pops:
                new_pop = init_pop(pop.name)
                new_pop.size = pop.size
                new_pop.age = pop.age + 1
                new_cell.pops.append(new_pop)
            for cap, value in old_cell.caps.items():
                new_cell.caps[cap] = value

    for cell in old_grid.watched_cells:
        new_grid.watched_cells.append(new_grid.cells[cell.x][cell.y])
    return new_grid


def init_pop(name):
    pop = Population(name)
    pop.increase = EFFECTS[name]['increase']
    pop.pressure = EFFECTS[name]['pressure']
    pop.migrate = EFFECTS[name]['migrate']
    return pop
