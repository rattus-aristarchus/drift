from src.logic.effects import util
from src.logic.entities.agents import agents

def brownian_migration(pop, cell):

    pass


def migrate(pop, cell):
    """
    Migrate pop living in cell.
    """

    cells_and_pops = []
    for neighbor in cell.neighbors:
        target_pop = neighbor.get_pop(pop.name)
        if target_pop:
            cells_and_pops.append((neighbor, target_pop))

    for cell, target_pop in cells_and_pops:
        draw = calculate_draw(pop.last_copy, target_pop.last_copy)
        barrier = calculate_barrier(pop.last_copy, target_pop.last_copy, cell.last_copy)

        _move_amount(pop, target_pop, draw, barrier)

        for res in pop.owned_resources:
            target_res = target_pop.get_resource(res.name)

            if not target_res:
                new_res = util.factory.new_resource(res.name, cell)
                agents.set_ownership(target_pop, new_res)
                target_res = new_res

            _move_amount(res, target_res, draw, barrier)



def calculate_draw(pop, target_pop):
    result = target_pop.get_fulfilment() - pop.get_fulfilment()
    return result


def calculate_barrier(pop, target_pop, target_cell):
    return pop.mobility


def _move_amount(entity, target, draw, barrier):
    amount = round(entity.last_copy.size * draw * barrier)
    entity.size -= amount
    target.size += amount


# TODO: this was written in the middle of the night
# because I couldn't sleep, so needs to be checked,
# and also extended to work for nomads
def producer_mig(pop, cell_buffer, grid_buffer):
    food_need = pop.last_copy.get_need("food")

    if food_need.actual < food_need.per_1000:
        # note: this only looks for one resource
        old_destinations = util.get_neighbors_with_res(
            pop.looks_for[0],
            cell_buffer.cell.last_copy.neighbors
        )
        destinations = util.find_equivalent_cells(old_destinations, grid_buffer.grid)

        if len(destinations) > 0:
            _migrate_pop(pop, destinations, pop.last_copy.size, 0.2)
       #     for destination in destinations:
       #         _set_migrate_flag_for_neighbors(pop, destination)

"""
def _set_migrate_flag_for_neighbors(pop, cell):
    possible_destinations = util.filter_positive_draw(pop, cell.neighbors)
    for dest in possible_destinations:
"""

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
