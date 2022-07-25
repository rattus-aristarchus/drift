import random
from kivy.logger import Logger

import data.effects as effects
from data.effects import EFFECTS, CellBuffer, GridBuffer
from data.base_types import Grid, Cell, Population


def generate_basic():
    width = 20
    height = 20
    map = Grid(width, height)

    rand_start_nomad(map)
    rand_start_nomad(map)
    rand_start_nomad(map)
    rand_start_rice(map)
    rand_start_rice(map)
    rand_start_rice(map)

    return map


def rand_start_nomad(map):
    start_a = rand_cell(map)
    pop = init_pop("коптеводы")
    pop.size = 1000
    start_a.pops.append(pop)
#    pop = init_pop("огнерунники")
#    pop.number = 10000
#    start_a.pops.append(pop)


def rand_start_rice(map):
    start_a = rand_cell(map)
    pop = init_pop("рисоводы")
    pop.size = 1000
    start_a.pops.append(pop)


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
    return new_grid


def do_turn_cell_old(cell, grid):
    neighbors = effects.get_neighbors(cell.x, cell.y, grid)
    this_and_neighbors = neighbors + [cell]

    for neighbor in neighbors:
        for pop in neighbor.pops:
            if pop.migrate is not None:
                pop.migrate(pop, cell, grid)

    for pop in cell.pops:
        if pop.increase is not None:
            pop.increase(pop, cell, grid)

    for pop in cell.pops:
        if pop.pressure is not None:
            pop.pressure(pop, cell, grid)


def init_pop(name):
    pop = Population(name)
    pop.increase = EFFECTS[name]['increase']
    pop.pressure = EFFECTS[name]['pressure']
    pop.migrate = EFFECTS[name]['migrate']
    return pop