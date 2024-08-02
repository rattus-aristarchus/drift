import sys
from kivy import Logger
from src.logic.effects import util
from src.logic.entities import agents


def produce(pop, cell_buffer, grid_buffer):

    product_vs_share_vs_surplus = []
    for product_model in pop.model.produces:
        entry = [
            product_model.name,
            pop.effort[product_model.name],
            _get_surplus_per_effort(product_model, pop)
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


def _get_surplus_per_effort(product_model, pop):
    pass


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


def agriculture(pop, product_model, cell):
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
