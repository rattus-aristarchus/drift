from kivy import Logger

import src.logic.entities.agents.ownership
from src.logic.effects import util
from src.logic.entities.agents import ownership

_log_name = __name__.split('.')[-1]

"""
def producer_grow(pop, cell_buffer, grid_buffer):
    num = pop.last_copy.size
    cap = util.get_cap_for_pop(pop, cell_buffer.cell.last_copy)

    pop.size += util.growth_with_capacity(num, cap, pop.yearly_growth)
"""


def natural_growth(res, cell):
    num = res.last_copy.size
    capacity = cell.last_copy.biome.get_capacity(res.name)

    res.size += util.growth_with_capacity(num, capacity, res.yearly_growth)


def growth(res):
    old_res = res.last_copy
    growth = old_res.yearly_growth
    num = old_res.size

    res.size += round(num * growth)

    for owner, amount in old_res.owners.items():
        res.owners[owner] += round(amount * growth)
        # TODO: здесь из-за округления суммы будут не сходиться


def producer_grow(pop):
    num = pop.last_copy.size
    growth_rate = pop.yearly_growth
    food_need = pop.last_copy.get_need("food")
    hunger = 1 - food_need.actual / food_need.per_1000

    if hunger <= 0:
        change = round(num * growth_rate)
    else:
        change = - round(hunger * num / 2)

    pop.size += change


def do_food(pop, cell):
    food_list = []
    ttl_food = 0

    for resource in pop.last_copy.owned_resources:
        if resource.type == "food":
            food_list.append(resource)
            ttl_food += resource.size

    needs = pop.last_copy.size

    if pop.last_copy.age == 0:
        sated = 1
        surplus = 0
    elif needs < ttl_food:
        sated = 1
        surplus = ttl_food - needs
    elif ttl_food < 0:
        sated = 0
        surplus = 0
    else:
        sated = ttl_food / needs
        surplus = 0

    surplus_obj = util.get_or_create_res('surplus', cell)
    surplus_obj.size += surplus
    ownership.add_ownership(pop, surplus_obj, surplus)

    food_need = pop.get_need("food")
    food_need.actual = sated * 1000

    Logger.debug(f"{_log_name}: {pop.name} in ({cell.x},{cell.y}) ate {ttl_food - surplus}, "
                 f"surplus is {str(surplus)}, satiation is {str(round(sated, 2))} (0-1)")
