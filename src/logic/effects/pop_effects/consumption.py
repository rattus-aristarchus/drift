from kivy import Logger
from src.logic.effects import util

"""
def producer_grow(pop, cell_buffer, grid_buffer):
    num = pop.last_copy.size
    cap = util.get_cap_for_pop(pop, cell_buffer.cell.last_copy)

    pop.size += util.growth_with_capacity(num, cap, pop.yearly_growth)
"""


def producer_grow(pop, cell_buffer, grid_buffer):
    num = pop.last_copy.size
    growth_rate = pop.model.yearly_growth
    food_need = pop.last_copy.get_need("food")
    hunger = 1 - food_need.fulfilment / food_need.per_1000

    if hunger <= 0:
        change = round(num * growth_rate)
    else:
        change = - round(hunger * num / 2)

    pop.size += change


def do_food(pop, cell_buffer, grid_buffer):
    food_list = []
    ttl_food = 0

    for resource in pop.last_copy.owned_resources:
        if resource.type == "food":
            food_list.append(resource)
            ttl_food += resource.size

    needs = pop.last_copy.size

    if pop.last_copy.age == 0:
        fulfilment = 1
        surplus = 0
    elif needs < ttl_food:
        fulfilment = 1
        surplus = ttl_food - needs
    elif ttl_food < 0:
        fulfilment = 0
        surplus = 0
    else:
        fulfilment = ttl_food / needs
        surplus = 0

    surplus_obj = util.get_or_create_res('surplus', cell_buffer.cell)
    surplus_obj.size += surplus

    food_need = pop.get_need("food")
    food_need.fulfilment = fulfilment * 1000

    Logger.debug(f"{__name__}: {pop.name} ate {ttl_food - surplus}, "
                 f"surplus is {str(surplus)}, hunger fulfilled by {str(round(fulfilment, 2))} (0-1)")