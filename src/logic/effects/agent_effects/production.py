import math

from src.logic.effects import effects_util
from src.logic.entities.agents import ownership
from src.logger import CustomLogger

logger = CustomLogger(__name__)

def produce(pop_write, pop_read, cell_write, cell_read, buffer):
    labor = effects_util.factory.new_resource("labor")
    labor.size = pop_read.size

    for output_name, target in pop_read.produces.items():
        prototype = effects_util.factory.prototype_resource(output_name)
        if not prototype:
            logger.error(f"{pop_read.name} is trying to produce "
                         f"{output_name}, which is a non-existent resource")
            continue

        production_from_resource(pop_write, pop_read, cell_write, cell_read, prototype, labor, buffer, target)


def production_from_resource(pop_write, pop_read, cell_write, cell_read, prototype, labor, buffer, target):
    land_name = prototype.land[0]
    # TODO: не учитывает собственность на землю; искать надо у популяции а не клетки;
    land_read = cell_read.get_res(land_name)
    # без земли делать нечего
    if not land_read:
        return None

    max_output, output_per_labor, message = _calculate_max_output(labor, pop_read, land_read, prototype, buffer, target)
    actual_size = _inputs_suffice_for(pop_read, cell_read, prototype, max_output)
    _reduce_inputs(prototype, pop_write, cell_write, labor, actual_size)
    output = _update_output(prototype, pop_write, cell_write, actual_size)
    if output_per_labor > 0:
        labor.size -= math.ceil(actual_size / output_per_labor)

    logger.debug(
        f"{pop_read.size} {pop_read.name} from ({cell_read.x},{cell_read.y}) "
        f"{message}"
        f"produced {actual_size} {prototype.name} ({output_per_labor} per labor)"
    )

    return output


def _reduce_inputs(prototype, pop_write, cell_write, labor, amount):
    for input_name, per_unit in prototype.inputs.items():
        res = cell_write.get_res(input_name)

        consumed = amount * per_unit
        ownership.subtract_ownership(pop_write, res, consumed)
        res.size -= consumed

    labor.size -= amount


def _inputs_suffice_for(pop_read, cell_read, prototype, max_output):
    current_max = max_output
    for input_name, per_unit in prototype.inputs.items():
        input_amount = effects_util.get_owned_amount(input_name, pop_read, cell_read)
        if input_amount < current_max * per_unit:
            current_max = math.floor(input_amount / per_unit)
    return current_max


def _update_output(prototype, pop_write, cell_write, output):
    product = cell_write.get_res(prototype.name)
    if not product:
        product = effects_util.factory.prototype_resource(prototype.name)

    product.size += output
    ownership.add_ownership(pop_write, product, output)
    return product


def _calculate_max_output(labor, pop_read, land_read, prototype, buffer, target):
    labor_num = labor.size
    if land_read and labor_num > 0:
        land_size = land_read.size
        labor_per_land = labor_num / land_size

        # если земли слишком много, ее не пытаются обработать:
        if labor_per_land < land_read.min_labor:
            labor_per_land = land_read.min_labor
        land_used = labor_num / labor_per_land
        productivity = _get_productivity(pop_read, land_read, prototype)
        limit = _get_output_limit(land_read, buffer, productivity)

        output = _hyperbolic_function(limit, labor_per_land, land_used)
        output_per_labor = output / labor_num
        output = _correct_for_target(pop_read, prototype, output, target)

    else:
        output = 0
        output_per_labor = 0
        land_size = 0
        land_used = 0
        limit = 0
        productivity = 0

    message = (
        f"with {round(land_used)} "
        f"{land_read.name} (of total {land_size}) and {round(limit, 3)} limit (with "
        f"{round(productivity, 3)} productivity) "
    )

    return output, output_per_labor, message


def _correct_for_target(pop_read, prototype, output, target):
    result = output
    match target:
        case "max":
            pass
        case "need":
            need = pop_read.get_need(need_type=prototype.type)
            if not need:
                result = 0
            else:
                result = round(need.per_1000 * pop_read.size / 1000)

    return result

# вот тут вопрос. стоит ли различать трудосберегающие технологии
# и трудоинтенсивные технологии? первое можно преставить как
# коэффициент, который тупо умножает общий результат, второе -
# как увеличение limit
def _hyperbolic_function(limit, labor_per_land, land_used):
    output_per_land = - limit / (labor_per_land + 1) + limit
    return round(output_per_land * land_used)


def _get_output_limit(resource, buffer, productivity):
    """
    Производительность ресурса при предельной загрузке рабочей силой.
    Рассчитывается как естественная производительность * производительность
    инструментов.
    """

    result = resource.max_output * productivity

    if resource.type == "land":
        # если речь об обработке земли, нужно учесть влияние температуры
        # ищем текущее отклонение температуры от средней для региона
        deviation_factor = buffer.memory["temp_deviation"] / buffer.world.deviation_50
        if deviation_factor >= 0:
            result *= (1 + deviation_factor)
        else:
            result *= (1 / 1 - deviation_factor)

    return result


def _get_productivity(pop, land, prototype):
    """
    Производительность средств производства и земли.
    """

    result = 1

    result *= land.productivity
    result *= _get_tool_productivity(pop, prototype)

    return result


def _get_tool_productivity(pop, prototype):
    """
    Производительность инструмента взвешена их доступностью
    (количество инструментов на количество рабочих рук)
    """

    result = 1

    for input_type in prototype.tools:
        # рассчитываем общее количество и среднюю производительность для
        # всех инструментов, подходящих под нужный тип
        ttl_available = 0
        ttl_productivity = 0
        for resource in pop.owned_resources:
            if resource.type == input_type:
                ttl_available += resource.size
                ttl_productivity += resource.size * resource.productivity

        # доступность - сколько человек обеспечено инструментами
        availability = ttl_available / pop.size
        if availability > 1:
            availability = 1

        if ttl_available == 0:
            avg_productivity = 0
        else:
            avg_productivity = ttl_productivity / ttl_available
        # если производительность инструмента 2, и он есть у 50%
        # населения, то производительность должна вырасти в 1.5 раза
        result *= avg_productivity * availability

    return result