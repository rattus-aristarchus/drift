"""
Общее правило: все чтения состояния должны производиться из
состояния предшествующего хода, запись состояния делается
в текущий ход. Таким образом, последовательность выполнения
эффектов в данном ходу не влияет на результат.

All data for the functions are taken from the grid of the previous turn.
This is done in order to avoid a situation where several cells are pulled from the
new grid, and some of those cells have already had changes applied to
them, while others haven't.
"""
import sys

from kivy import Logger
from src.logic.effects import util
from src.logic.entities import agents


def get_effect(func_name):
    """
    This function is injected into modules that need to use
    effect. Don't worry about it.
    """
    return eval(func_name)


"""
def producer_grow(pop, cell_buffer, grid_buffer):
    num = pop.last_copy.size
    cap = util.get_cap_for_pop(pop, cell_buffer.cell.last_copy)

    pop.size += util.growth_with_capacity(num, cap, pop.yearly_growth)
"""


def producer_grow(pop, cell_buffer, grid_buffer):
    num = pop.last_copy.size
    growth_rate = pop.model.yearly_growth
    hunger = pop.last_copy.hunger

    if hunger <= 0:
        change = round(num * growth_rate)
    else:
        change = - round(hunger * num / 2)

    pop.size += change


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


def produce(pop, cell_buffer, grid_buffer):
    # предполагаем, что эти уже выстроены по приоритету
    # надо вначале вычислить приоритет
 #   remaining_labor = pop.last_copy.size
  #  for product, priority in pop.model.produces.items():
     #   _get_max_effort()
      #  if product.type == "food":
      #      do_agriculture(pop, product, cell_buffer.cell)
      #  elif product.type == "industry":
      #      do_industry(pop, product, cell_buffer.cell)

    do_agriculture(pop, pop.last_copy.model.produces[0], cell_buffer.cell)

def _get_max_effort(product_model, ttl_labor, cell):
    """
    Вычисляем, сколько максимум труда может занять
    производство product_model
    """
    if_infinite_inputs = product_model.max_labor_share * ttl_labor

    bottleneck_num = sys.maxsize
    for input in product_model.inputs:
        resource = cell.get_res(input.id)
        can_use_labor = input.max_labor * resource.size
        if can_use_labor < bottleneck_num:
            bottleneck_num = can_use_labor

    if bottleneck_num < if_infinite_inputs:
        return bottleneck_num
    else:
        return if_infinite_inputs


def do_industry(pop, product_model, cell):
    pass


def do_agriculture(pop, product_model, cell):
    land_name = product_model.inputs[0].id
    old_land = cell.last_copy.get_res(land_name)

    people_num = pop.last_copy.size
    if old_land:
        land_size = old_land.size
        labor_per_land = people_num / land_size
        # если земли слишком много, ее не пытаются обработать:
        if labor_per_land < old_land.model.min_labor:
            labor_per_land = old_land.model.min_labor
        land_used = people_num / labor_per_land
        limit = old_land.model.max_labor

        output = hyperbolic_function(limit, labor_per_land, land_used)
    else:
        land_size = 0
        land_used = 0
        output = 0

    product = util.get_or_create_res(product_model.id, cell)
    product.size = output
    agents.set_ownership(pop, product)

    land = cell.get_res(land_name)
    agents.set_ownership(pop, land, land_used)

    Logger.debug(f"{__name__}: {pop.name} of size {str(people_num)} with {str(round(land_used))} "
                 f"land (of total {land_size} land) produced {str(output)}")


def hyperbolic_function(limit, labor_per_land, land_used):
    output_per_land = - limit / (labor_per_land + 1) + limit
    return round(output_per_land * land_used)


def do_food(pop, cell_buffer, grid_buffer):
    food_list = []
    ttl_food = 0

    for resource in pop.last_copy.owned_resources:
        if resource.type == "food":
            food_list.append(resource)
            ttl_food += resource.size

    needs = pop.last_copy.size

    if pop.last_copy.age == 0:
        hunger = 0
        surplus = 0
    elif needs < ttl_food:
        hunger = 0
        surplus = ttl_food - needs
    elif ttl_food < 0:
        hunger = 1
        surplus = 0
    else:
        hunger = 1 - ttl_food / needs
        surplus = 0

    surplus_obj = util.get_or_create_res('surplus', cell_buffer.cell)
    surplus_obj.size = surplus

    pop.hunger = hunger

    Logger.debug(f"{__name__}: {pop.name} ate {ttl_food - surplus}, "
                 f"surplus is {str(surplus)}, hunger is {str(round(hunger, 2))} (0-1)")
