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
    cap = cell_buffer.cell.biome['capacity'][pop.name]
    slowing = (1.0 - pop.size / cap)
    if slowing < 0:
        slowing = 0
    pop.size += round(pop.size * 0.1 * slowing)
    Logger.debug("new pop number " + str(pop.size))


def nomad_dec(pop, cell_buffer, grid_buffer):
    # pressure for soot nomads is all neighboring rice growers
    this_and_neighbors = cell_buffer.old_neighbors + [cell_buffer.old_cell]
    sum_ricegrowers = sum_for_cells("рисоводы", this_and_neighbors)
    decrease = round(sum_ricegrowers * 0.1)
    Logger.debug("decreasing soot nomads by " + str(decrease))
    pop.size -= decrease


def nomad_mig(pop, cell_buffer, grid_buffer):
    if pop.size > 1000:
        for neighbor in cell_buffer.neighbors:
            check_pop = get_or_create_pop(pop.name, neighbor)
            cap = neighbor.biome['capacity'][pop.name]
            slowing = (1.0 - check_pop.size / cap)
            if slowing < 0:
                slowing = 0
            growth = round(grid_buffer.all_sootnomads * 0.001 * slowing)
            check_pop.size += growth


def rice_inc(pop, cell_buffer, grid_buffer):
    Logger.debug("growing pop " + pop.name + ", current number " + str(pop.size))
    cap = cell_buffer.cell.biome['capacity'][pop.name]
    slowing = (1.0 - pop.size / cap)
    if slowing < 0:
        slowing = 0
    growth = round(pop.size * 0.1 * slowing)
    pop.size += growth
    Logger.debug("new pop number " + str(pop.size))


def rice_dec(pop, cell_buffer, grid_buffer):
    if has_neighbor_sootnomad(cell_buffer.old_neighbors):
        decrease = round(grid_buffer.all_sootnomads * 0.01)
        pop.size -= decrease


def rice_mig(pop, cell_buffer, grid_buffer):
    if pop.size > 1000:
        for neighbor in cell_buffer.neighbors:
            check_pop = get_or_create_pop(pop.name, neighbor)
            cap = neighbor.biome['capacity'][pop.name]
            slowing = (1.0 - check_pop.size / cap)
            if slowing < 0:
                slowing = 0
            growth = round(pop.size * 0.01 * slowing)
            check_pop.size += growth


EFFECTS = {
    "огнерунники": {
        'increase': flamesheep_inc,
        'pressure': flamesheep_dec,
        'migrate': None
    },
    "коптеводы": {
        'increase': nomad_inc,
        'pressure': nomad_dec,
        'migrate': nomad_mig
    },
    "рисоводы": {
        'increase': rice_inc,
        'pressure': rice_dec,
        'migrate': rice_mig
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
        check_pop = Population(name)
        cell.pops.append(check_pop)
    return check_pop