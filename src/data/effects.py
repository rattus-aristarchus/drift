"""
All data for the functions are taken from the grid of the previous turn.
This is done in order to avoid a situation where several cells are pulled from the
new grid, and some of those cells have already had changes applied to
them, while others haven't.
"""


import math
from random import Random
from kivy.logger import Logger

from util import CONST
import data.base_types as base_types
from data.base_types import Population, Group


class GridBuffer:

    def __init__(self, grid, old_grid):
        self.grid = grid
        self.old_grid = old_grid
        self.all_sootnomads = sum_for_cells('soot_nomads', old_grid.cells_as_list())


class CellBuffer:

    def __init__(self, cell, grid_buffer):
        self.cell = cell
        self.old_cell = grid_buffer.old_grid.cells[cell.x][cell.y]
        self.neighbors = get_neighbors(cell.x, cell.y, grid_buffer.grid)
        self.old_neighbors = get_neighbors(cell.x, cell.y, grid_buffer.old_grid)

        # self.nomad_capacity = round(get_pop_num('steppe_grass', cell) / 10 - get_pop_num('soot_nomads', cell))
        # self.wheatmen_capacity = round(get_pop_num('wheat', cell) / 2 - get_pop_num('wheatmen', cell))


def add_effects(agent, type, name):
    func_names = CONST[type][name]['effects']
    for func_name in func_names:
        agent.effects.append(eval(func_name))


"""
The effect functions
"""


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
    sum_ricegrowers = sum_for_cells('rice_growers', this_and_neighbors)
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


# the simulation for rats and lynxes is based on the Lotka-Volterra model
def rat_inc(pop, cell_buffer, grid_buffer):
    rat_num = get_pop_num('крысы', cell_buffer.old_cell)
    lynx_num = get_pop_num('рыси', cell_buffer.old_cell)
    capacity = cell_buffer.old_cell.caps['крысы']

    natural = rat_num * 0.4 * (1 - pop.size / capacity)
    predation = rat_num * lynx_num / 10000
    # for rats, natural change is growth
    growth = round(natural - predation)
    pop.size += growth
    Logger.debug("Number of rats increased by " + str(growth) + " to " + str(pop.size))


def lynx_inc(pop, cell_buffer, grid_buffer):
    rat_num = get_pop_num('rats', cell_buffer.old_cell)
    lynx_num = get_pop_num('lynxes', cell_buffer.old_cell)
    capacity = cell_buffer.old_cell.caps['крысы']

    natural = lynx_num * 0.5 * (1 - pop.size / capacity)
    predation = lynx_num * rat_num / 20000
    # for lynxes, natural change (i.e. with no rats)
    # is decrease
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
        best_destinations = get_neighbors_with_lowest_density(pop.name, cell_buffer.old_neighbors)
        random = Random().randrange(0, len(best_destinations))
        best_destination = best_destinations[random]
        best_destination = grid_buffer.grid.cells[best_destination.x][best_destination.y]
        pop_at_destination = get_or_create_pop(pop.name, best_destination)
        migration = round((pop.size / capacity) * num * 0.2)
        pop.size -= migration
        pop_at_destination.size += migration


def sparse_nomad_inc(pop, cell_buffer, grid_buffer):
    num = get_pop_num('soot_nomads', cell_buffer.old_cell)
    grass_num = get_pop_num('steppe_grass', cell_buffer.old_cell)
    capacity = grass_num * 0.1
    if capacity == 0:
        capacity = 0.1
    natural = round(num * 0.05 * (1 - pop.size / capacity))
    pop.size += natural


def sparse_nomad_press(pop, cell_buffer, grid_buffer):
    neighbors_and_this = [cell_buffer.cell] + cell_buffer.neighbors
    num = get_pop_num('soot_nomads', cell_buffer.old_cell)

    #for cell in neighbors_and_this:
    grass_num = get_pop_num('steppe_grass', cell_buffer.old_cell)
    protected_num = grass_num - 5000 if grass_num > 5000 else 0
    decrease = round(num * protected_num / 8000)
    grass_pop = get_or_create_pop('steppe_grass', cell_buffer.cell)
    grass_pop.size -= decrease


def sparse_nomad_mig(pop, cell_buffer, grid_buffer):
    # first, we check if the population has exceeded half capacity
    num = get_pop_num('soot_nomads', cell_buffer.old_cell)
    grass_num = get_pop_num('steppe_grass', cell_buffer.old_cell)
    capacity = grass_num / 10

    if num > capacity / 3:
        # if it has, time to migrate. choose a destination

        def get_free_capacity(cell):
            num_nomad = get_pop_num('soot_nomads', cell)
            num_grass = get_pop_num('steppe_grass', cell)
            return round(num_grass / 10 - num_nomad)

        def choose_destination(sorted_destinations):
            # if the top destinations are equal, we choose between them
            # randomly
            best = [sorted_destinations[-1]]
            free_cap = get_free_capacity(sorted_destinations[-1])
            for i in range(-2, -len(destinations), -1):
                free_cap_check = get_free_capacity(sorted_destinations[i])
                if free_cap_check < free_cap:
                    break
                else:
                    best.append(sorted_destinations[i])
            random = Random().randrange(0, len(best))
            return best[random]

        destinations = order_neighbors_by(get_free_capacity, cell_buffer.old_neighbors)
        dest_0_old = choose_destination(destinations)
        destinations.remove(dest_0_old)
        dest_1_old = choose_destination(destinations)

        # since we're getting data from the old grid, we now have
        # to get corresponding cells from the new grid
        destination = grid_buffer.grid.cells[dest_0_old.x][dest_0_old.y]
        destination_1 = grid_buffer.grid.cells[dest_1_old.x][dest_1_old.y]

        # if the destination is still too crowded, the band
        # splits in two. otherwise, it migrates to the destination
        if num > get_free_capacity(dest_0_old) / 2:
            new_pop = cell_buffer.cell.create_pop('soot_nomads')
            new_pop.size = round(pop.size / 2)
            pop.size = round(pop.size / 2)

            base_types.arrive_and_merge(new_pop, destination)
            base_types.migrate_and_merge(pop, cell_buffer.cell, destination_1)
        else:
            base_types.migrate_and_merge(pop, cell_buffer.cell, destination)


def wheatmen_inc(pop, cell_buffer, grid_buffer):
    num = get_pop_num('wheatmen', cell_buffer.old_cell)
    wheat_num = get_pop_num('wheat', cell_buffer.old_cell)
    capacity = wheat_num * 0.5
    if capacity == 0:
        capacity = 0.1
    natural = round(num * 0.1 * (1 - pop.size / capacity))
    Logger.debug("wheatmen_inc: natural increase for wheatmen is " + str(natural))
    pop.size += natural


def wheatmen_press(pop, cell_buffer, grid_buffer):
    num = get_pop_num('wheatmen', cell_buffer.old_cell)

    # if not part of a community, farmers form a village
    if pop.group is None:
        village = cell_buffer.cell.create_group('settlement')
        pop.group = village
        village.pops.append(pop)

    # farmers farm
    wheat_planted = num * 10
    wheat_capacity = cell_buffer.old_cell.caps['wheat']
    wheat_inc = round(wheat_planted * (1 - wheat_planted / wheat_capacity))
    Logger.debug("wheatmen_press: wheatmen have planted " + str(wheat_inc) + " wheat")
    get_or_create_pop('wheat', cell_buffer.cell).size += wheat_inc

    # farmers also reduce available grass for grazing
    grass_num = get_pop_num('steppe_grass', cell_buffer.old_cell)
    if not grass_num == 0:
        grass_capacity = cell_buffer.old_cell.caps['steppe_grass']
        # let's assume grass and wheat compete for the same space;
        # so wheat at full capacity means there's not space for grass
        # and vice versa
        overcrowding = wheat_planted / wheat_capacity + grass_num / grass_capacity - 1
        if overcrowding > 0:
            grass = cell_buffer.cell.get_pop('steppe_grass')
            grass.size -= round(grass_num * overcrowding)


def wheatmen_mig(pop, cell_buffer, grid_buffer):
    # first, we check if the population is approaching capacity
    num = get_pop_num('wheatmen', cell_buffer.old_cell)
    wheat_num = get_pop_num('wheat', cell_buffer.old_cell)
    wheat_cap = cell_buffer.old_cell.caps['wheat']

    if num > wheat_cap / 50:
        # if it has, time to migrate. choose a destination

        def get_free_capacity(cell):
            num = get_pop_num('wheatmen', cell)
            wheat_cap = cell_buffer.old_cell.caps['wheat']
            return round(wheat_cap / 50 - num)

        def choose_destination(sorted_destinations):
            for i in range(-1, -len(sorted_destinations), -1):
                whos_territory = get_group('settlement', sorted_destinations[i])
                if whos_territory is not None:
                    sorted_destinations.remove(sorted_destinations[i])

            # if the top destinations are equal, we choose between them
            # randomly
            best = [sorted_destinations[-1]]
            free_cap = get_free_capacity(sorted_destinations[-1])
            for i in range(-2, -len(sorted_destinations), -1):
                free_cap_check = get_free_capacity(sorted_destinations[i])
                if free_cap_check < free_cap:
                    break
                else:
                    best.append(sorted_destinations[i])
            random = Random().randrange(0, len(best))
            return best[random]

        destinations = order_neighbors_by(get_free_capacity, cell_buffer.old_neighbors)
        dest_0_old = choose_destination(destinations)

        # since we're getting data from the old grid, we now have
        # to get corresponding cells from the new grid
        destination = grid_buffer.grid.cells[dest_0_old.x][dest_0_old.y]
        dest_pop = get_or_create_pop('wheatmen', destination)
        migrated_amount = round(num * 0.05)
        pop.size -= migrated_amount
        dest_pop.size += migrated_amount
        dest_wheat = get_or_create_pop('wheat', destination)
        dest_wheat.size += migrated_amount * 2


def grass_grow(pop, cell_buffer, grid_buffer):
    num = get_pop_num('steppe_grass', cell_buffer.old_cell)
    capacity = cell_buffer.old_cell.caps['steppe_grass']
    natural = round(num * 0.1 * (1 - pop.size / capacity))
    pop.size += natural


def wheat_grow(pop, cell_buffer, grid_buffer):
    num = get_pop_num('wheat', cell_buffer.old_cell)
    pop.size -= num


def settlement(group, cell_buffer, grid_buffer):
    # expand the borders
    if len(group.territory) == 1:
        for neighbor in cell_buffer.neighbors:
            random = Random().randrange(0, 1)
            if random > 0.25:
                base_types.add_territory(neighbor, group)

    # TODO: so here we obviously need a more fundamental mechanism for
    # how the farmers would expand into more territory

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
        check_pop = cell.create_pop(name)
    return check_pop


def get_pop_num(pop_name, cell):
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
        num = get_pop_num(pop_name, neighbor)
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