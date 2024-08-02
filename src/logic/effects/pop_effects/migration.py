from src.logic.effects import util


# TODO: this was written in the middle of the night
# because I couldn't sleep, so needs to be checked,
# and also extended to work for nomads
def producer_mig(pop, cell_buffer, grid_buffer):
    if pop.last_copy.hunger > 0:
        # note: this only looks for one resource
        old_destinations = util.get_neighbors_with_res(pop.model.looks_for[0], cell_buffer.old_neighbors)
        destinations = util.find_equivalent_cells(old_destinations, grid_buffer.grid)

        if len(destinations) > 0:
            _migrate_pop(pop, destinations, pop.last_copy.size, 0.2)


def _migrate_pop(pop, destinations, old_size, fraction_to_migrate):
    migrants = round(old_size * fraction_to_migrate)
    per_dest = round(migrants / len(destinations))

    pop.size -= migrants
    for destination in destinations:
        new_pop = util.get_or_create_pop(pop.name, destination)
        new_pop.size += per_dest


def _migrate_res(res, destinations, old_size, fraction_to_migrate):
    migrants = round(old_size * fraction_to_migrate)
    per_dest = round(migrants / len(destinations))

    res.size -= migrants
    for destination in destinations:
        new_res = util.get_or_create_res(res.name, destination)
        new_res.size += per_dest