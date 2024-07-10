import math

from kivy import Logger

from src.data import cells


def get_group(name, cell):
    result = None
    for group in cell.groups:
        if group.name == name:
            result = group
            break
    return result


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
        check_pop = cells.create_pop(cell, name)
    return check_pop


def get_pop_size(pop_name, cell):
    pop = cell.get_pop(pop_name)
    if pop is None:
        num = 0
    else:
        num = pop.size
    return num


def get_neighbors_with_lowest_density(pop_name, neighbors):
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


def get_neighbors_with_highest(pop_name, neighbors):
    highest_num = 0
    highest_cells = []
    for neighbor in neighbors:
        num = get_pop_size(pop_name, neighbor)
        if num == highest_num:
            highest_cells.append(neighbor)
        elif num > highest_num:
            highest_num = num
            highest_cells = [neighbor]
    return highest_cells


def order_neighbors_by(retreive_parameter, neighbors):
    """
    Sort the cells in the neighbors list in ascending order by the
    retreive parameter function.
    """
    ordered = []

    for neighbor in neighbors:
        size = retreive_parameter(neighbor)

        for i in range(len(ordered)):
            check_size = retreive_parameter(ordered[i])
            if size <= check_size:
                ordered.insert(i, neighbor)
                break
        if neighbor not in ordered:
            ordered.append(neighbor)

    return ordered


def order_neighbors_by_descending(retreive_parameter, neighbors):
    """
    Sort the cells in the neighbors list in descending order by the
    retreive parameter function.
    """

    ordered = []

    for neighbor in neighbors:
        size = retreive_parameter(neighbor)

        for i in range(len(ordered)):
            check_size = retreive_parameter(ordered[i])
            if size >= check_size:
                ordered.insert(i, neighbor)
                break
        if neighbor not in ordered:
            ordered.append(neighbor)

    return ordered


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

