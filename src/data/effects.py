from kivy.logger import Logger

from data.base_types import Population


def flamesheep_inc(pop, cell, grid):
    pass


def flamesheep_dec(pop, cell, grid):
    pass


def nomad_inc(pop, cell, grid):
    neighbors = get_neighbors(cell.x, cell.y, grid)

    # natural growth
    Logger.debug("growing pop " + pop.name + ", current number " + str(pop.number))
    cap = cell.biome['capacity'][pop.name]
    slowing = (1.0 - pop.number / cap)
    if slowing < 0:
        slowing = 0
    growth = round(pop.number * 0.1 * slowing)
    pop.number += growth
    Logger.debug("new pop number " + str(pop.number))


def nomad_dec(pop, cell, grid):
    # pressure for soot nomads is all neighboring rice growers
    this_and_neighbors = get_neighbors(cell.x, cell.y, grid) + [cell]
    sum_ricegrowers = sum_for_cells("рисоводы", this_and_neighbors)
    decrease = round(sum_ricegrowers * 0.1)
    Logger.debug("decreasing soot nomads by " + str(decrease))
    pop.number -= decrease


def nomad_mig(pop, cell, grid):
    if pop.number > 1000:
        # this might affect performance
        sum_sootnomads = sum_for_cells("коптеводы", grid.cells_as_list())

        check_pop = get_or_create_pop(pop.name, cell)
        cap = cell.biome['capacity'][pop.name]
        slowing = (1.0 - check_pop.number / cap)
        if slowing < 0:
            slowing = 0
        growth = round(sum_sootnomads * 0.001 * slowing)
        check_pop.number += growth


def rice_inc(pop, cell, grid):
    Logger.debug("growing pop " + pop.name + ", current number " + str(pop.number))
    cap = cell.biome['capacity'][pop.name]
    slowing = (1.0 - pop.number / cap)
    if slowing < 0:
        slowing = 0
    growth = round(pop.number * 0.1 * slowing)
    pop.number += growth
    Logger.debug("new pop number " + str(pop.number))


def rice_dec(pop, cell, grid):
    sum_sootnomads = sum_for_cells("коптеводы", grid.cells_as_list())
    decrease = round(sum_sootnomads * 0.01)
    pop.number -= decrease


def rice_mig(pop, cell, grid):
    if pop.number > 1000:
        check_pop = get_or_create_pop(pop.name, cell)
        cap = cell.biome['capacity'][pop.name]
        slowing = (1.0 - check_pop.number / cap)
        if slowing < 0:
            slowing = 0
        growth = round(pop.number * 0.01 * slowing)
        check_pop.number += growth


EFFECTS = {
    "огнерунники": {
        "inc": flamesheep_inc,
        "pres": flamesheep_dec
    },
    "коптеводы": {
        "inc": nomad_inc,
        "pres": nomad_dec
    },
    "рисоводы": {
        "inc": rice_inc,
        "pres": rice_dec
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


def has_neighbor_sootnomad():
    for next in neighbors:
        nomads = next.get_pop("коптеводы")
        if nomads is not None and nomads.age > 0:
            return True
    return False
"""


def sum_for_cells(pop_name, cells):
    result = 0
    for neighbor in cells:
        pop = neighbor.get_pop(pop_name)
        if pop is not None:
            Logger.debug("found neighboring " + pop.name + ", numbering " + str(pop.number) +
                         " in cell x " + str(neighbor.x) + ", y " + str(neighbor.y))
            result += pop.number
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
