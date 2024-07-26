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

from src.logic.effects import util


def get_effect(func_name):
    """
    This function is injected into modules that need to use
    effect. Don't worry about it.
    """
    return eval(func_name)


def producer_grow(pop, cell_buffer, grid_buffer):
    num = util.get_pop_size(pop.name, cell_buffer.old_cell)
    cap = util.get_cap_for_pop(pop, cell_buffer.old_cell)

    pop.size += util.growth_with_capacity(num, cap, pop.yearly_growth)


def producer_mig(pop, cell_buffer, grid_buffer):
    num = util.get_pop_size(pop.name, cell_buffer.old_cell)

    # тут вопрос. мы меряем пока станет тесно кочевникам или овцам? пока кочевникам
    cap = util.get_cap_for_pop(pop, cell_buffer.old_cell)

    if num > cap / 2:

        res_to_migrate = []
        for food_name in pop.sustained_by.keys():
            sustains_pop = cell_buffer.cell.get_res(food_name)
            if sustains_pop:
                res_to_migrate.append(sustains_pop)

        # a list of all cells where the main pop has
        # something to sustain it
        all_destinations = []

        for res_to_migrate in res_to_migrate:
            old_destinations = util.get_available_neighbors(res_to_migrate.name, cell_buffer.old_neighbors)
            destinations = util.find_equivalent_cells(old_destinations, grid_buffer.grid)
            old_size = util.get_res_size(res_to_migrate.name, cell_buffer.old_cell)
            _migrate_res(res_to_migrate, destinations, old_size, 0.2)

            for destination in destinations:
                if destination not in all_destinations:
                    all_destinations.append(destination)

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
