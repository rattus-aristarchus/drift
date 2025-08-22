from kivy import Logger

import src.logic.entities.agents.ownership
from src.logic.effects import effects_util
from src.logic.entities.agents import ownership

_log_name = __name__.split('.')[-1]

"""
def producer_grow(pop, cell_buffer, grid_buffer):
    num = pop.last_copy.size
    cap = effects_util.get_cap_for_pop(pop, cell_buffer.cell.last_copy)

    pop.size += effects_util.growth_with_capacity(num, cap, pop.yearly_growth)
"""


def natural_growth(res_write, res_read, cell_write, cell_read):
    num = res_read.size
    capacity = cell_read.biome.get_capacity(res_read.name)

    res_write.size += effects_util.growth_with_capacity(num, capacity, res_read.yearly_growth)


def growth(res_write, res_read):
    growth = res_read.yearly_growth
    num = res_read.size

    res_write.size += round(num * growth)

    for owner, amount in res_read.owners.items():
        res_write.owners[owner] += round(amount * growth)
        # TODO: здесь из-за округления суммы будут не сходиться


def producer_grow(pop_write, pop_read, cell_write, cell_read):
    num = pop_read.size
    growth_rate = pop_read.yearly_growth
    food_need = pop_read.get_need("food")
    hunger = 1 - food_need.actual / food_need.per_1000

    if hunger <= 0:
        change = round(num * growth_rate)
    else:
        change = - round(hunger * num / 2)

    pop_write.size += change

    Logger.debug(
        f"{_log_name}: a population of {pop_read.name} from "
        f"({cell_read.x},{cell_read.y}) increased from {pop_read.size} "
        f"to {pop_write.size} due to hunger being {hunger}."
    )


def do_food(pop_write, pop_read, cell_write, cell_read):
    food_list = []
    ttl_food = 0

    for resource in pop_read.owned_resources:
        if resource.type == "food":
            food_list.append(resource)
            ttl_food += resource.size

    needs = pop_read.size

    if pop_read.age == 0:
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

    food_need = pop_write.get_need("food")
    food_need.actual = sated * 1000

    Logger.debug(f"{_log_name}: {pop_read.name} in ({cell_read.x},{cell_read.y}) ate {ttl_food - surplus}, "
                 f"surplus is {surplus}, satiation is {round(sated, 2)} (0-1)")
