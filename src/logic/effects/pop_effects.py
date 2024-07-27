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
from kivy import Logger
from src.logic.effects import util


def get_effect(func_name):
    """
    This function is injected into modules that need to use
    effect. Don't worry about it.
    """
    return eval(func_name)


def producer_grow_old(pop, cell_buffer, grid_buffer):
    num = pop.last_copy.size
    cap = util.get_cap_for_pop(pop, cell_buffer.cell.last_copy)

    pop.size += util.growth_with_capacity(num, cap, pop.yearly_growth)


def producer_grow(pop, cell_buffer, grid_buffer):
    num = pop.last_copy.size
    growth_rate = pop.model.yearly_growth
    hunger = pop.last_copy.hunger

    if hunger <= 0:
        change = round(num * growth_rate)
    else:
        change = - round(hunger * num / 2)

    pop.size += change


def producer_mig(pop, cell_buffer, grid_buffer):
    num = pop.last_copy.size

    # тут вопрос. мы меряем пока станет тесно кочевникам
    # или овцам? пока кочевникам
    cap = util.get_cap_for_pop(pop, cell_buffer.cell.last_copy)

    # если численность приближается к потолку, мигрируем
    if num > cap / 2:

        # какие ресурсы можем взять с собой
        res_to_migrate = []
        for food_name in pop.sustained_by.keys():
            sustains_pop = cell_buffer.cell.get_res(food_name)
            if sustains_pop:
                res_to_migrate.append(sustains_pop)

        # a list of all cells where the main pop has
        # something to sustain it
        all_destinations = []

        # мигрируем каждый ресурс
        for res_to_migrate in res_to_migrate:
            old_destinations = util.get_available_neighbors(res_to_migrate.name, cell_buffer.old_neighbors)
            destinations = util.find_equivalent_cells(old_destinations, grid_buffer.grid)

            if len(destinations) > 0:
                old_size = util.get_res_size(res_to_migrate.name, cell_buffer.cell.last_copy)
                _migrate_res(res_to_migrate, destinations, old_size, 0.2)

            for destination in destinations:
                if destination not in all_destinations:
                    all_destinations.append(destination)

        # мигрируем саму популяцию
        if len(all_destinations) > 0:
            _migrate_pop(pop, all_destinations, num, 0.2)


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


def agricultural_output(pop, cell_buffer, grid_buffer):
    product_model = pop.model.produces[0]
    land_name = product_model.inputs[0].id
    land = cell_buffer.cell.last_copy.get_res(land_name)
    people = pop.last_copy.size

    if product_model.id in pop.sustained_by.keys():
        need_per_person = pop.sustained_by[product_model.id]
    else:
        need_per_person = 0

    if land:
        land_size = land.size
        labor_per_land = people / land_size
        # если земли слишком много, ее не пытаются обработать:
        if labor_per_land < 1:
            labor_per_land = 1
            land_used = people
        else:
            land_used = land_size
        optimum = land.model.optimum_labor

        output_per_land = - round(optimum / labor_per_land) + optimum + 1
        output = output_per_land * land_used

        # subtract needs
        needs = need_per_person * people
        if needs < output:
            hunger = 0
            surplus = output - needs
        elif output < 0:
            hunger = 1
            surplus = 0
        else:
            hunger = 1 - output / needs
            surplus = 0
    else:
        land_size = 0
        land_used = 0
        output = 0
        surplus = 0
        hunger = 1

    product = util.get_or_create_res(product_model.id, cell_buffer.cell)
    product.size = output

    surplus_obj = util.get_or_create_res('surplus', cell_buffer.cell)
    surplus_obj.size = surplus

    pop.hunger = hunger

    land.set_owner(pop, land_used)

    Logger.debug(f"{__name__}: {pop.name} of size {str(people)} with {str(land_used)} "
                 f"land (total land: {land_size}) produced {str(output)}; surplus "
                 f"{str(surplus)}, hunger {str(hunger)}")

