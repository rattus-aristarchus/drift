import sys
from kivy import Logger

import src.logic.entities.agents.agents
from src.logic.effects import util
from src.logic.effects.util import factory


def produce_for_surplus(pop, cell_buffer, grid_buffer):
    """
    Это недописанная и совершенно непроверенная функция.
    Производство на рынок. Мысль: сравниваем излишек на
    вложенные усилия, и перераспределяем усилия туда,
    где больше излишка.
    """

    #TODO: это надо переписать, т. к. модели используются теперь только для io
    product_vs_share_vs_surplus = []
    for product_name in pop.produces:
        entry = [
            product_name,
            pop.effort[product_name],
            _get_surplus_per_effort(product_name, pop)
        ]
        product_vs_share_vs_surplus.append(entry)

    # сортируем по убыванию доли затрачиваемого труда
    sorted(product_vs_share_vs_surplus, key=lambda lst: lst[1], reverse=True)

    last_surplus = sys.maxsize
    for product, share, surplus in product_vs_share_vs_surplus:
        if surplus > last_surplus:
            _shrink_everyones_share_except(product_vs_share_vs_surplus, product, 0.1)
            share += 0.1

        last_surplus = surplus


def _shrink_everyones_share_except(product_vs_share_vs_surplus, to_except, total_shrink):
    shrink_per_product = total_shrink / len(product_vs_share_vs_surplus)
    for product, share, surplus in product_vs_share_vs_surplus:
        if not product == to_except:
            share -= shrink_per_product


def _get_surplus_per_effort(product_name, pop):
    pass


def _get_max_effort(product_name, ttl_labor, cell):
    """
    Вычисляем, сколько максимум труда может занять
    производство product_model
    """
    prototype = factory.prototype_resource(product_name)

    if_infinite_inputs = prototype.max_labor_share * ttl_labor

    bottleneck_num = sys.maxsize
    for input in prototype.inputs:
        resource = cell.get_res(input)
        res_prototype = factory.prototype_resource(input)
        can_use_labor = res_prototype.max_labor * resource.size
        if can_use_labor < bottleneck_num:
            bottleneck_num = can_use_labor

    if bottleneck_num < if_infinite_inputs:
        return bottleneck_num
    else:
        return if_infinite_inputs


def produce(pop, cell, grid_buffer):
    for output in pop.produces:
        if not output:
            pass
        prototype = util.factory.prototype_resource(output)
        if prototype.type == "food":
            natural_resource_exploitation(pop, prototype, cell, grid_buffer)
        elif prototype.type == "tools":
            natural_resource_exploitation(pop, prototype, cell, grid_buffer)


def natural_resource_exploitation(pop, prototype, cell, grid_buffer):
    land_name = prototype.inputs[0]
    old_land = cell.last_copy.get_res(land_name)
    # без земли делать нечего
    if not old_land:
        return

    people_num = pop.last_copy.size
    if old_land:
        land_size = old_land.size
        labor_per_land = people_num / land_size
        # если земли слишком много, ее не пытаются обработать:
        if labor_per_land < old_land.min_labor:
            labor_per_land = old_land.min_labor
        land_used = people_num / labor_per_land
        tech_factor = get_tech_factor(pop.last_copy)
        limit = _resource_productivity(old_land, grid_buffer, tech_factor)

        output = hyperbolic_function(limit, labor_per_land, land_used)
    else:
        land_size = 0
        land_used = 0
        limit = 0
        output = 0
        tech_factor = 0

    product = util.get_or_create_res(prototype.name, cell)
    product.size += output
    src.logic.entities.agents.agents.set_ownership(pop, product)

    land = cell.get_res(land_name)
    src.logic.entities.agents.agents.set_ownership(pop, land, land_used)

    Logger.debug(f"{__name__}: {pop.name} of size {str(people_num)} with {str(round(land_used))} "
                 f"{land_name} (of total {land_size}) and {str(limit)} productivity cap (with "
                 f"{str(tech_factor)} tech factor) produced "
                 f"{str(output)} {prototype.name}")


# вот тут вопрос. стоит ли различать трудосберегающие технологии
# и трудоинтенсивные технологии? первое можно преставить как
# коэффициент, который тупо умножает общий результат, второе -
# как увеличение limit
def hyperbolic_function(limit, labor_per_land, land_used):
    output_per_land = - limit / (labor_per_land + 1) + limit
    return round(output_per_land * land_used)


def _resource_productivity(resource, grid_buffer, tech_factor):
    result = resource.max_labor * tech_factor

    if resource.type == "land":
        deviation_factor = grid_buffer.temp_deviation / grid_buffer.history.world.deviation_50
        if deviation_factor >= 0:
            result *= (1 + deviation_factor)
        else:
            result *= (1 / 1 - deviation_factor)

    return result


def get_tech_factor(pop):
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
