"""
All data for the functions are taken from the grid of the previous turn.
This is done in order to avoid a situation where several cells are pulled from the
new grid, and some of those cells have already had changes applied to
them, while others haven't.
"""


import math
from random import Random
from kivy.logger import Logger

from data.base_types import Population


class GridBuffer:

    def __init__(self, grid, old_grid):
        self.grid = grid
        self.old_grid = old_grid
        self.all_sootnomads = sum_for_cells("коптеводы", old_grid.cells_as_list())


class CellBuffer:

    def __init__(self, cell, grid_buffer):
        self.cell = cell
        self.old_cell = grid_buffer.old_grid.cells[cell.x][cell.y]
        self.neighbors = get_neighbors(cell.x, cell.y, grid_buffer.grid)
        self.old_neighbors = get_neighbors(cell.x, cell.y, grid_buffer.old_grid)


def flamesheep_inc(pop, cell_buffer, grid_buffer):
    pass


def flamesheep_dec(pop, cell_buffer, grid_buffer):
    pass


def flamesheep_dec(pop, cell_buffer, grid_buffer):
    pass


def nomad_inc(pop, cell_buffer, grid_buffer):
    # natural growth
    Logger.debug("growing pop " + pop.name + ", current number " + str(pop.size))
    cap = cell_buffer.cell.caps[pop.name]
    slowing = (1.0 - pop.size / cap)
#    if slowing < 0:
#        slowing = 0
    pop.size += round(pop.size * 0.1 * slowing)
    Logger.debug("new pop number " + str(pop.size))


def nomad_pressure(pop, cell_buffer, grid_buffer):
    # pressure for soot nomads is all neighboring rice growers
    this_and_neighbors = cell_buffer.old_neighbors + [cell_buffer.old_cell]
    sum_ricegrowers = sum_for_cells("рисоводы", this_and_neighbors)
    decrease = round(sum_ricegrowers * 0.1)

    # effects of over-grazing. current population reduces the cap; if the
    # cap is too low, it starts regenerating
    overgrazing = round(pop.size * 0.4)
    max_cap = cell_buffer.cell.biome['capacity'][pop.name]
    cur_cap = cell_buffer.cell.caps[pop.name]
    recovery = (max_cap / cur_cap) * (0.1 * max_cap)

    Logger.debug("decreasing soot nomads by " + str(decrease))
    pop.size -= decrease
    cell_buffer.cell.caps[pop.name] -= overgrazing - recovery


def nomad_mig(pop, cell_buffer, grid_buffer):
    if pop.size > 1000:
        for neighbor in cell_buffer.neighbors:
            check_pop = get_or_create_pop(pop.name, neighbor)
            cap = neighbor.caps[pop.name]
            slowing = (1.0 - check_pop.size / cap)
            if slowing < 0:
                slowing = 0
            growth = round(grid_buffer.all_sootnomads * 0.001 * slowing)
            check_pop.size += growth


def rice_inc(pop, cell_buffer, grid_buffer):
    Logger.debug("growing pop " + pop.name + ", current number " + str(pop.size))
    cap = cell_buffer.cell.caps[pop.name]
    slowing = (1.0 - pop.size / cap)
 #   if slowing < 0:
  #      slowing = 0
    growth = round(pop.size * 0.1 * slowing)
    pop.size += growth
    Logger.debug("new pop number " + str(pop.size))


def rice_pressure(pop, cell_buffer, grid_buffer):
    if has_neighbor_sootnomad(cell_buffer.old_neighbors):
        decrease = round(grid_buffer.all_sootnomads * 0.01)
        pop.size -= decrease


def rice_mig(pop, cell_buffer, grid_buffer):
    if pop.size > 1000:
        for neighbor in cell_buffer.neighbors:
            check_pop = get_or_create_pop(pop.name, neighbor)
            cap = neighbor.caps[pop.name]
            slowing = (1.0 - check_pop.size / cap)
            if slowing < 0:
                slowing = 0
            growth = round(pop.size * 0.01 * slowing)
            check_pop.size += growth


def rat_inc(pop, cell_buffer, grid_buffer):
    rat_num = get_pop_num('крысы', cell_buffer.old_cell)
    lynx_num = get_pop_num('рыси', cell_buffer.old_cell)
    capacity = cell_buffer.old_cell.caps['крысы']

    natural = rat_num * 0.4 * (1 - pop.size / capacity)
    predation = rat_num * lynx_num / 10000
    growth = round(natural - predation)
    pop.size += growth
    Logger.debug("Number of rats increased by " + str(growth) + " to " + str(pop.size))


def lynx_inc(pop, cell_buffer, grid_buffer):
    rat_num = get_pop_num('крысы', cell_buffer.old_cell)
    lynx_num = get_pop_num('рыси', cell_buffer.old_cell)
    capacity = cell_buffer.old_cell.caps['крысы']

    natural = lynx_num * 0.5 * (1 - pop.size / capacity)
    predation = lynx_num * rat_num / 20000
    growth = round(predation - natural)
    pop.size += growth
    Logger.debug("Number of lynxes increased by " + str(growth) + " to " + str(pop.size))


def migrate(pop, cell_buffer, grid_buffer):
    num = get_pop_num(pop.name, cell_buffer.old_cell)
    capacity = cell_buffer.old_cell.caps[pop.name]
    if num > capacity / 2:
        # Since data is based on the old grid, we have to calculate
        # the best neighbor based on old neighbors; but since we'll
        # be applying changes to the new grid, we need to immediately
        # get the equivalent cell from the new grid
        best_destinations = get_neighbor_with_lowest(pop.name, cell_buffer.old_neighbors)
        random = Random().randrange(0, len(best_destinations))
        best_destination = best_destinations[random]
        best_destination = grid_buffer.grid.cells[best_destination.x][best_destination.y]
        pop_at_destination = get_or_create_pop(pop.name, best_destination)
        migration = round((pop.size / capacity) * num * 0.2)
        pop.size -= migration
        pop_at_destination.size += migration


def do_nothing(pop, cell_buffer, grid_buffer):
    pass


EFFECTS = {
    "огнерунники": {
        'increase': flamesheep_inc,
        'pressure': flamesheep_dec,
        'migrate': do_nothing
    },
    "коптеводы": {
        'increase': nomad_inc,
        'pressure': nomad_pressure,
        'migrate': nomad_mig
    },
    "рисоводы": {
        'increase': rice_inc,
        'pressure': rice_pressure,
        'migrate': rice_mig
    },
    "крысы": {
        'increase': rat_inc,
        'pressure': do_nothing,
        'migrate': migrate
    },
    "рыси": {
        'increase': lynx_inc,
        'pressure': do_nothing,
        'migrate': migrate
    }
}

"""
def has_empty_neighbor(name):
    for next in neighbors:
        if next.get_pop(name) is None:
            return True
    return False


def has_neighbor(name):
    for next in neighbors:
        if next.get_pop(name) is not None:
            return True
    return False
"""


def has_neighbor_sootnomad(neighbors):
    for next in neighbors:
        nomads = next.get_pop("коптеводы")
        if nomads is not None:
            return True
    return False


def sum_for_cells(pop_name, cells):
    result = 0
    for neighbor in cells:
        pop = neighbor.get_pop(pop_name)
        if pop is not None:
            Logger.debug("found neighboring " + pop.name + ", numbering " + str(pop.size) +
                         " in cell x " + str(neighbor.x) + ", y " + str(neighbor.y))
            result += pop.size
    return result


def get_neighbors(x, y, grid):
    result = []

    poss_x_rng = [x - 1, x, x + 1]
    poss_y_rng = [y - 1, y, y + 1]

    for poss_x in poss_x_rng:
        for poss_y in poss_y_rng:
            if poss_x == x and poss_y == y:
                continue
            if poss_x < 0 or poss_x >= grid.width:
                continue
            if poss_y < 0 or poss_y >= grid.height:
                continue
            result.append(grid.cells[poss_x][poss_y])

    return result


def get_or_create_pop(name, cell):
    check_pop = cell.get_pop(name)
    if check_pop is None:
        check_pop = init_pop(name)
        cell.pops.append(check_pop)
    return check_pop


def get_pop_num(pop_name, cell):
    pop = cell.get_pop(pop_name)
    if pop is None:
        num = 0
    else:
        num = pop.size
    return num


def get_neighbor_with_lowest(pop_name, neighbors):
    lowest_density = math.inf
    lowest_cells = []
    for neighbor in neighbors:
        cap = neighbor.caps[pop_name]
        pop = neighbor.get_pop(pop_name)
        if pop is not None:
            density = pop.size / cap
        else:
            density = 0

        if density == lowest_density:
            lowest_cells.append(neighbor)
        elif density < lowest_density:
            lowest_density = density
            lowest_cells = [neighbor]
    return lowest_cells


# This is a sign of spaghetti code (an identical function is present
# in control), but right now i can't think of a good way to fix it
def init_pop(name):
    pop = Population(name)
    pop.increase = EFFECTS[name]['increase']
    pop.pressure = EFFECTS[name]['pressure']
    pop.migrate = EFFECTS[name]['migrate']
    return pop
