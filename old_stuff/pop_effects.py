import src.logic.entities.structures


def flamesheep_inc(pop, cell_buffer, grid_buffer):
    pass


def flamesheep_dec(pop, cell_buffer, grid_buffer):
    pass


def flamesheep_dec(pop, cell_buffer, grid_buffer):
    pass


def nomad_inc(pop, cell_buffer, grid_buffer):
    # natural growth
    Logger.debug("growing pop " + pop.name + ", current number " + str(pop.size))
    cap = cell_buffer.cell.biome.get_capacity(pop.name)
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
    max_cap = cell_buffer.cell.biome.get_capacity(pop.name)
    cur_cap = cell_buffer.cell.biome.get_capacity(pop.name)
    recovery = (max_cap / cur_cap) * (0.1 * max_cap)

    Logger.debug("decreasing soot nomads by " + str(decrease))
    pop.size -= decrease
    cell_buffer.cell.biome.capacity[pop.name] -= overgrazing - recovery


def nomad_mig(pop, cell_buffer, grid_buffer):
    if pop.size > 1000:
        for neighbor in cell_buffer.neighbors:
            check_pop = get_or_create_pop(pop.name, neighbor)
            cap = neighbor.biome.get_capacity(pop.name)
            slowing = (1.0 - check_pop.size / cap)
            if slowing < 0:
                slowing = 0
            growth = round(grid_buffer.all_sootnomads * 0.001 * slowing)
            check_pop.size += growth


def rice_inc(pop, cell_buffer, grid_buffer):
    Logger.debug("growing pop " + pop.name + ", current number " + str(pop.size))
    cap = cell_buffer.cell.biome.get_capacity(pop.name)
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
            cap = neighbor.biome.get_capacity(pop.name)
            slowing = (1.0 - check_pop.size / cap)
            if slowing < 0:
                slowing = 0
            growth = round(pop.size * 0.01 * slowing)
            check_pop.size += growth


# the simulation for rats and lynxes is based on the Lotka-Volterra model
def rat_inc(pop, cell_buffer, grid_buffer):
    rat_num = get_pop_size('крысы', cell_buffer.old_cell)
    lynx_num = get_pop_size('рыси', cell_buffer.old_cell)
    capacity = cell_buffer.old_cell.biome.get_capacity('крысы')

    natural = rat_num * 0.4 * (1 - pop.size / capacity)
    predation = rat_num * lynx_num / 10000
    # for rats, natural change is growth
    growth = round(natural - predation)
    pop.size += growth
    Logger.debug("Number of rats increased by " + str(growth) + " to " + str(pop.size))


def lynx_inc(pop, cell_buffer, grid_buffer):
    rat_num = get_pop_size('rats', cell_buffer.old_cell)
    lynx_num = get_pop_size('lynxes', cell_buffer.old_cell)
    capacity = cell_buffer.old_cell.biome.get_capacity('крысы')

    natural = lynx_num * 0.5 * (1 - pop.size / capacity)
    predation = lynx_num * rat_num / 20000
    # for lynxes, natural change (i.e. with no rats)
    # is decrease
    growth = round(predation - natural)
    pop.size += growth
    Logger.debug("Number of lynxes increased by " + str(growth) + " to " + str(pop.size))


def migrate(pop, cell_buffer, grid_buffer):
    num = get_pop_size(pop.name, cell_buffer.old_cell)
    capacity = cell_buffer.old_cell.biome.get_capacity(pop.name)
    if num > capacity / 2:
        # Since data is based on the old grid, we have to calculate
        # the best neighbor based on old neighbors; but since we'll
        # be applying changes to the new grid, we need to immediately
        # get the equivalent cell from the new grid
        best_destinations = get_neighbors_with_lowest_density(pop.name, cell_buffer.old_neighbors)
        random = Random().randrange(0, len(best_destinations))
        best_destination_old = best_destinations[random]
        best_destination = grid_buffer.grid.cells[best_destination_old.x][best_destination_old.y]
        pop_at_destination = get_or_create_pop(pop.name, best_destination)
        migration = round((pop.size / capacity) * num * 0.2)
        pop.size -= migration
        pop_at_destination.size += migration


def sparse_nomad_inc(pop, cell_buffer, grid_buffer):
    num = get_pop_size('soot_nomads', cell_buffer.old_cell)
    if num < 0:
        num = 0
    grass_num = get_pop_size('steppe_grass', cell_buffer.old_cell)
    capacity = grass_num * 0.1
    if capacity <= 0:
        capacity = 0.1

    if num <= capacity:
        natural = round(num * 0.05 * (1 - num / capacity))
    else:
        natural = - round((num - capacity) / 2)
    pop.size += natural


def sparse_nomad_press(pop, cell_buffer, grid_buffer):
    neighbors_and_this = [cell_buffer.cell] + cell_buffer.neighbors
    num = get_pop_size('soot_nomads', cell_buffer.old_cell)

    #for cell in neighbors_and_this:
    grass_num = get_pop_size('steppe_grass', cell_buffer.old_cell)
    protected_num = grass_num - 5000 if grass_num > 5000 else 0
    decrease = round(num * protected_num / 8000)
    grass_pop = get_or_create_pop('steppe_grass', cell_buffer.cell)
    grass_pop.size -= decrease


def sparse_nomad_mig(pop, cell_buffer, grid_buffer):
    # first, we check if the population has exceeded half capacity
    num = get_pop_size('soot_nomads', cell_buffer.old_cell)
    grass_num = get_pop_size('steppe_grass', cell_buffer.old_cell)
    capacity = grass_num / 10

    if num > capacity / 3:
        # if it has, time to migrate. choose a destination

        def get_free_capacity(cell):
            num_nomad = get_pop_size('soot_nomads', cell)
            num_grass = get_pop_size('steppe_grass', cell)
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
            model = util.model_base.get_pop('soot_nomads')
            new_pop = agents.create_pop('soot_nomads', cell_buffer.cell)
            new_pop.size = round(pop.size / 2)
            pop.size = round(pop.size / 2)

            cells.arrive_and_merge(new_pop, destination)
            cells.migrate_and_merge(pop, cell_buffer.cell, destination_1)
        else:
            cells.migrate_and_merge(pop, cell_buffer.cell, destination)


def wheatmen_inc(pop, cell_buffer, grid_buffer):
    num = get_pop_size('wheatmen', cell_buffer.old_cell)
    wheat_num = get_pop_size('wheat', cell_buffer.old_cell)
    capacity = wheat_num * 0.5
    if capacity == 0:
        capacity = 0.1
    natural = round(num * 0.1 * (1 - pop.size / capacity))
    Logger.debug("wheatmen_inc: natural increase for wheatmen is " + str(natural))
    pop.size += natural


def wheatmen_press(pop, cell_buffer, grid_buffer):
    num = get_pop_size('wheatmen', cell_buffer.old_cell)

    # if not part of a community, farmers form a village
    if len(pop.structures) == 0:
        model = util.model_base.get_structure('settlement')
        village = src.logic.entities.structures.create_structure(model, cell_buffer.cell)
        pop.structures.append(village)
        village.pops.append(pop)

    # farmers farm
    wheat_planted = num * 10
    wheat_capacity = cell_buffer.old_cell.biome.get_capacity('wheat')
    wheat_inc = round(wheat_planted * (1 - wheat_planted / wheat_capacity))
    Logger.debug("wheatmen_press: wheatmen have planted " + str(wheat_inc) + " wheat")
    get_or_create_pop('wheat', cell_buffer.cell).size += wheat_inc

    # farmers also reduce available grass for grazing
    grass_num = get_pop_size('steppe_grass', cell_buffer.old_cell)
    if not grass_num == 0:
        grass_capacity = cell_buffer.old_cell.biome.get_capacity('steppe_grass')
        # let's assume grass and wheat compete for the same space;
        # so wheat at full capacity means there's not space for grass
        # and vice versa
        overcrowding = wheat_planted / wheat_capacity + grass_num / grass_capacity - 1
        if overcrowding > 0:
            grass = cell_buffer.cell.get_pop('steppe_grass')
            grass.size -= round(grass_num * overcrowding)


def wheatmen_mig(pop, cell_buffer, grid_buffer):
    # first, we check if the population is approaching capacity
    num = get_pop_size('wheatmen', cell_buffer.old_cell)
    wheat_num = get_pop_size('wheat', cell_buffer.old_cell)
    wheat_cap = cell_buffer.old_cell.biome.get_capacity('wheat')

    if num > wheat_cap / 50:
        # if it has, time to migrate. choose a destination

        def get_free_capacity(cell):
            num = get_pop_size('wheatmen', cell)
            wheat_cap = cell_buffer.old_cell.biome.get_capacity('wheat')
            return round(wheat_cap / 50 - num)

        def choose_destination(sorted_destinations):
            # if the top destinations are equal, we choose between them
            # randomly. unfortunately, we can't take just the first in the
            # list, since with zeroes ties will occur often and the bias will
            # be significant
            best = [sorted_destinations[-1]]
            free_cap = get_free_capacity(sorted_destinations[-1])
            for i in range(len(sorted_destinations)):
                free_cap_check = get_free_capacity(sorted_destinations[i])
                if free_cap_check < free_cap:
                    break
                else:
                    best.append(sorted_destinations[i])
            random = Random().randrange(0, len(best))
            return best[random]

        def filter_occupied(destinations):
            filtered = []
            for i in range(len(destinations)):
                whos_territory = get_structure('settlement', destinations[i])
                if whos_territory is None:
                    filtered.append(destinations[i])
            return filtered

        destinations = util.order_neighbors_by_descending(get_free_capacity, cell_buffer.old_neighbors)
        destinations = filter_occupied(destinations)

        # if everything is occupied, no point continuing
        if len(destinations) > 0:
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
    num = get_pop_size('steppe_grass', cell_buffer.old_cell)
    capacity = cell_buffer.old_cell.biome.get_capacity('steppe_grass')
    natural = round(num * 0.1 * (1 - pop.size / capacity))
    pop.size += natural


def wheat_grow(pop, cell_buffer, grid_buffer):
    num = get_pop_size('wheat', cell_buffer.old_cell)
    pop.size -= num
