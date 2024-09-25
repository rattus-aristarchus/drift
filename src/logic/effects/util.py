import math
from kivy import Logger
from src.logic.entities.agents import populations, resources
from src.logic.entities.factories import Factory

# эта штука выставляется статически при запуске программы
factory: Factory = None


def get_structure(name, cell):
    result = None
    for structure in cell.structures:
        if structure.name == name:
            result = structure
            break
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
        check_pop = factory.new_population(name)
        cell.pops.append(check_pop)
    return check_pop


def get_or_create_res(name, cell):
    check_res = cell.get_res(name)
    if check_res is None:
        check_res = factory.new_resource(name)
        cell.resources.append(check_res)
    return check_res


def get_pop_size(pop_name, cell):
    pop = cell.get_pop(pop_name)
    if pop is None:
        num = 0
    else:
        num = pop.size
    return num


def get_res_size(res_name, cell):
    res = cell.get_res(res_name)
    if res is None:
        num = 0
    else:
        num = res.size
    return num


def get_neighbors_with_lowest_density(pop_name, neighbors):
    lowest_density = math.inf
    lowest_cells = []
    for neighbor in neighbors:
        cap = neighbor.biome.get_capacity(pop_name)
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


def get_neighbors_with_pop_capacity(pop_name, neighbors):
    result = []
    for neighbor in neighbors:
        if pop_name in neighbor.biome.capacity.keys():
            result.append(neighbor)
    return result


def get_neighbors_with_res(res_name, neighbors):
    result = []
    for neighbor in neighbors:
        res = neighbor.get_res(res_name)
        if res and res.get_free_amount() > 0:
            result.append(neighbor)
    return result


def find_equivalent_cells(cells, grid):
    result = []
    for cell in cells:
        new_cell = grid.cells[cell.x][cell.y]
        result.append(new_cell)
    return result


def growth_with_capacity(number, capacity, growth):
    # growth is a fraction of 1
    if capacity <= 0:
        capacity = 1
    if number <= 0:
        return 0

    if number <= capacity:
        result = round(number * growth * (1 - number / capacity))
    else:
        result = - round((number - capacity) / 2)
    return result


def get_cap_for_pop(pop, cell):
    """
    Returns the capacity of this cell for this population
    based on other populations this one is sustained by
    """
    ttl_cap = 0
    for food, food_index in pop.sustained_by.items():
        ttl_cap += round(cell.biome.get_capacity(food) / food_index)
    return ttl_cap
