import sys
from kivy import Logger

import src.logic.entities.agents.ownership
from src.logic.effects import effects_util
from src.logic.entities.agents import ownership

_log_name = __name__.split('.')[-1]

def produce(pop_write, pop_read, cell_write, cell_read, buffer):
    for output in pop_read.produces:
        if not output:
            pass
        prototype = effects_util.factory.prototype_resource(output)
        if prototype.type == "food":
            natural_resource_exploitation(pop_write, pop_read, cell_write, cell_read, prototype, buffer)
        elif prototype.type == "tools":
            natural_resource_exploitation(pop_write, pop_read, cell_write, cell_read, prototype, buffer)


def natural_resource_exploitation(pop_write, pop_read, cell_write, cell_read, prototype, buffer):
    land_name = prototype.inputs[0]
    old_land = cell_read.get_res(land_name)

    # без земли делать нечего
    if not old_land:
        return

    people_num = pop_read.size
    if old_land:
        land_size = old_land.size
        labor_per_land = people_num / land_size
        # если земли слишком много, ее не пытаются обработать:
        if labor_per_land < old_land.min_labor:
            labor_per_land = old_land.min_labor
        land_used = people_num / labor_per_land
        tech_factor = _get_tech_factor(pop_read)
        limit = _resource_productivity(old_land, buffer, tech_factor)

        output = _hyperbolic_function(limit, labor_per_land, land_used)
    else:
        land_size = 0
        land_used = 0
        limit = 0
        output = 0
        tech_factor = 0

    product = effects_util.get_or_create_res(prototype.name, cell_write)
    product.size += output
    ownership.set_ownership(pop_write, product)

    land = cell_write.get_res(land_name)
    ownership.set_ownership(pop_write, land, land_used)

    Logger.debug(f"{_log_name}: {people_num} {pop_write.name} from ({cell_write.x},{cell_write.y})  "
                 f"with {round(land_used)} "
                 f"{land_name} (of total {land_size}) and {round(limit, 3)} productivity cap (with "
                 f"{round(tech_factor, 3)} tech factor) produced "
                 f"{output} {prototype.name}")


# вот тут вопрос. стоит ли различать трудосберегающие технологии
# и трудоинтенсивные технологии? первое можно преставить как
# коэффициент, который тупо умножает общий результат, второе -
# как увеличение limit
def _hyperbolic_function(limit, labor_per_land, land_used):
    output_per_land = - limit / (labor_per_land + 1) + limit
    return round(output_per_land * land_used)


def _resource_productivity(resource, buffer, tech_factor):
    result = resource.max_labor * tech_factor

    if resource.type == "land":
        deviation_factor = buffer.memory["temp_deviation"] / buffer.world.deviation_50
        if deviation_factor >= 0:
            result *= (1 + deviation_factor)
        else:
            result *= (1 / 1 - deviation_factor)

    return result


def _get_tech_factor(pop):
    result = 1
    for resource in pop.owned_resources:
        if resource.type == "tools":
            availability = resource.size / pop.size
            if availability > 1:
                availability = 1
            # если производительность инструмента 2, и он есть у 50%
            # населения, то производительность должна вырости в 1.5 раза
            result += (resource.productivity - 1) * availability
    return result
