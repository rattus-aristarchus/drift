from src.logger import CustomLogger

import src.logic.entities.agents.ownership
from src.logic.effects import effects_util
from src.logic.entities.agents import ownership

logger = CustomLogger(__name__)


def natural_growth(res_write, res_read, cell_write, cell_read):
    num = res_read.size
    capacity = cell_read.biome.get_capacity(res_read.name)

    res_write.size += effects_util.growth_with_capacity(num, capacity, res_read.yearly_growth)


def growth(res_write, res_read):
    increase = round(res_read.size * res_read.yearly_growth)

    res_write.size += increase

    msg_owners = ""
    for owner, owned_amount in res_read.owners.items():
        increase = round(owned_amount * res_read.yearly_growth)
        res_write.owners[owner] += increase
        # TODO: здесь из-за округления суммы будут не сходиться
        msg_owners +=f"{owner}: {increase}\n"

    msg = f"resource {res_read.name} changed amount by {increase}, new size {res_write.size}"
    if len(msg_owners) > 0:
        msg += f"; affected owners:\n{msg_owners[:-1]}"
    logger.debug(
        msg
    )


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

    logger.debug(
        f"a population of {pop_read.name} from "
        f"({cell_read.x},{cell_read.y}) increased from {pop_read.size} "
        f"to {pop_write.size} due to hunger being {hunger}."
    )


def do_food(pop_write, pop_read, cell_write, cell_read):
    ttl_food = _count_food(pop_read)
    ttl_appetite = pop_read.size

    if pop_read.age == 0:
        sated = 1
        consumed = ttl_appetite
    elif ttl_appetite < ttl_food:
        sated = 1
        consumed = ttl_appetite
    else:
        sated = ttl_food / ttl_appetite
        consumed = ttl_food

    surplus = ttl_food - consumed
    food_need = pop_write.get_need("food")
    food_need.actual = sated * 1000

    _reduce_food(consumed, pop_write)

    logger.debug(f"{pop_read.name} in ({cell_read.x},{cell_read.y}) ate {ttl_food - surplus}, "
                 f"surplus is {surplus}, satiation is {round(sated, 2)} (0-1)")


def _count_food(pop_read):
    result = 0
    for resource in pop_read.owned_resources:
        if resource.type == "food":
            if pop_read.name not in resource.owners.keys():
                pass
            result += resource.owners[pop_read.name]
    return result


def _reduce_food(ttl_consumed, pop_write):
    to_subtract = ttl_consumed
    for resource in pop_write.owned_resources:
        if resource.type == "food":
            if resource.owners[pop_write.name] > to_subtract:
                subtracted = to_subtract
                resource.reduce_for_owner(pop_write, to_subtract)
            else:
                subtracted = resource.owners[pop_write.name]
                resource.set_for_owner(pop_write, 0)
            to_subtract -= subtracted
            if to_subtract <= 0:
                break