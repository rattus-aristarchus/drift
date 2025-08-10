import sys
from math import floor

from kivy import Logger

import src.logic.entities.agents.ownership
from src.logic.effects import effects_util
from src.logic.entities.agents import ownership

_log_name = __name__.split('.')[-1]

def produce(pop_write, pop_read, cell_write, cell_read, buffer):
    res_pool = []

    for output_name in pop_read.produces:
        if not output_name:
            pass

        prototype = effects_util.factory.prototype_resource(output_name)
        output = None
        if prototype.type == "food":
            output = production_from_resource(pop_write, pop_read, cell_write, cell_read, prototype, buffer, res_pool)
        elif prototype.type == "tools":
            output = production_from_resource(pop_write, pop_read, cell_write, cell_read, prototype, buffer, res_pool)
        elif prototype.type == "labor":
            output = create_labor(pop_write, pop_read, cell_write, cell_read, prototype)
        if output:
            res_pool.append(output)

    for output in res_pool:
        cell_write.resources.append(output)

    # проблема. у нас слишком много побочных эффектов из-за того что мы убираем ресурсы и в res_pool и в клетке
    # возможно, стоит вначале сложить все ресурсы в один список, чтобы дальше работать только с ним?



def create_labor(pop_write, pop_read, cell_write, cell_read, prototype):
    output_size = pop_read.size
    output = _create_output(prototype, pop_write, output_size)

    Logger.debug(f"{_log_name}: {pop_read.size} {pop_read.name} from ({cell_read.x},{cell_read.y})  "
                 f"worked {output_size} units of labor")

    return output


def production_from_resource(pop_write, pop_read, cell_write, cell_read, prototype, buffer, res_pool):
    land_name = prototype.land[0]
    # TODO: не учитывает собственность на землю; искать надо у популяции а не клетки;
    land_read = cell_read.get_res(land_name)
    # без земли делать нечего
    if not land_read:
        return None

    max_output, land_size, land_used, tech_factor, limit = _calculate_output(pop_read, land_read, buffer)
    output_size = _inputs_suffice_for(pop_read, cell_read, prototype, max_output, res_pool)
    _reduce_inputs(prototype, pop_write, cell_write, res_pool, output_size)
    output = _create_output(prototype, pop_write, output_size)

    # TODO: пока что у нас владеет землёй тот кто её обрабатывает
    land = cell_write.get_res(land_name)
    ownership.set_ownership(pop_write, land, land_used)

    Logger.debug(f"{_log_name}: {pop_read.size} {pop_read.name} from ({cell_read.x},{cell_read.y})  "
                 f"with {round(land_used)} "
                 f"{land_name} (of total {land_size}) and {round(limit, 3)} productivity cap (with "
                 f"{round(tech_factor, 3)} tech factor) produced "
                 f"{output_size} {prototype.name}")

    return output


def _reduce_inputs(prototype, pop_write, cell_write, res_pool, amount):
    for input_name, per_unit in prototype.inputs.items():
        res = cell_write.get_res(input_name)
        res_from_pool = _get_from_pool(input_name, res_pool)

        consumed = amount * per_unit
        if res_from_pool:
            if consumed > res_from_pool.size:
                ownership.subtract_ownership(pop_write, res_from_pool, res_from_pool.size)
                res_from_pool.size = 0
                consumed = 0
            else:
                ownership.subtract_ownership(pop_write, res_from_pool, consumed)
                res_from_pool -= consumed
                consumed -= res_from_pool

        if res:
            ownership.subtract_ownership(pop_write, res, consumed)
            res.size -= consumed


def _get_from_pool(name, resource_pool):
    for res in resource_pool:
        if res.name == name:
            return res

    return None


def _inputs_suffice_for(pop_read, cell_read, prototype, max_output, res_pool):
    current_max = max_output
    for input_name, per_unit in prototype.inputs.items():
        input_amount = effects_util.get_owned_amount(input_name, pop_read, cell_read)
        input_amount += effects_util.get_owned_amount_from_pool(input_name, pop_read, res_pool)
        if input_amount < current_max * per_unit:
            current_max = floor(input_amount / per_unit)
    return current_max


def _create_output(prototype, pop_write, output):
    product = effects_util.factory.new_resource(prototype.name)
    product.size += output
    ownership.set_ownership(pop_write, product)
    return product


def _calculate_output(pop_read, land_read, buffer):
    people_num = pop_read.size
    if land_read:
        land_size = land_read.size
        labor_per_land = people_num / land_size

        # если земли слишком много, ее не пытаются обработать:
        if labor_per_land < land_read.min_labor:
            labor_per_land = land_read.min_labor
        land_used = people_num / labor_per_land
        tech_factor = _get_tech_factor(pop_read)
        limit = _productivity_limit(land_read, buffer, tech_factor)

        output = _hyperbolic_function(limit, labor_per_land, land_used)
    else:
        output = 0
        land_size = 0
        land_used = 0
        limit = 0
        tech_factor = 0

    return output, land_size, land_used, tech_factor, limit


# вот тут вопрос. стоит ли различать трудосберегающие технологии
# и трудоинтенсивные технологии? первое можно преставить как
# коэффициент, который тупо умножает общий результат, второе -
# как увеличение limit
def _hyperbolic_function(limit, labor_per_land, land_used):
    output_per_land = - limit / (labor_per_land + 1) + limit
    return round(output_per_land * land_used)


def _productivity_limit(resource, buffer, tech_factor):
    """
    Производительность ресурса при предельной загрузке рабочей силой.
    Рассчитывается как естественная производительность * производительность
    инструментов.
    """

    result = resource.max_output * resource.productivity * tech_factor

    if resource.type == "land":
        # если речь об обработке земли, нужно учесть влияние температуры
        # ищем текущее отклонение температуры от средней для региона
        deviation_factor = buffer.memory["temp_deviation"] / buffer.world.deviation_50
        if deviation_factor >= 0:
            result *= (1 + deviation_factor)
        else:
            result *= (1 / 1 - deviation_factor)

    return result


def _get_tech_factor(pop):
    """
    Влияние средств производства на выпуск. Рассчитывается
    на основе количества инструментов и их производительности
    """

    result = 1
    # ищем инструменты
    for resource in pop.owned_resources:
        if resource.type == "tools":
            availability = resource.size / pop.size
            if availability > 1:
                availability = 1
            # если производительность инструмента 2, и он есть у 50%
            # населения, то производительность должна вырасти в 1.5 раза
            result += (resource.productivity - 1) * availability
    return result
