import random
from kivy.logger import Logger

import data.effects as effects
from data.effects import EFFECTS
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
    pop.number = 1000
    start_a.pops.append(pop)
    pop = init_pop("огнерунники")
    pop.number = 10000
    start_a.pops.append(pop)


def rand_start_rice(map):
    start_a = rand_cell(map)
    pop = init_pop("рисоводы")
    pop.number = 1000
    start_a.pops.append(pop)


def rand_cell(map):
    return map.cells[random.randint(0, map.width - 1)][random.randint(0, map.height - 1)]


def do_turn(old_grid):
    Logger.info("Grid: doing turn")
    new_grid = Grid(old_grid.width, old_grid.height)
    for x in range(0, old_grid.width):
        for y in range(0, old_grid.height):
            Logger.debug("doing cell " + str(x) + ", " + str(y))
            old_cell = old_grid.cells[x][y]
            new_cell = new_grid.cells[x][y]
            for pop in old_cell.pops:
                new_pop = init_pop(pop.name)
                new_pop.number = pop.number
                new_pop.age = pop.age + 1
                new_cell.pops.append(new_pop)
            do_turn_cell(new_cell, old_grid)
    return new_grid


def do_turn_cell(cell, grid):
    neighbors = effects.get_neighbors(cell.x, cell.y, grid)
    this_and_neighbors = neighbors + [cell]

    for neighbor in neighbors:
        for pop in neighbor.pops:
            if pop.migrate is not None:
                pop.migrate(pop, cell, grid)

    for pop in cell.pops:
        pop.increase(pop, cell, grid)

    for pop in cell.pops:
        pop.decrease(pop, cell, grid)

    # remove pops that have died out
    to_remove = []
    for pop in cell.pops:
        if pop.number <= 0:
            to_remove.append(pop)
    for pop in to_remove:
        cell.pops.remove(pop)


def init_pop(name):
    pop = Population(name)
    pop.increase = EFFECTS[name]['inc']
    pop.decrease = EFFECTS[name]['pres']
#    pop.migrate = EFFECTS[name]['mig']
    return pop