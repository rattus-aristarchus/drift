from src.logic.effects import util
from src.logic.entities.agents import agents
from kivy import Logger

_log_name = __name__.split('.')[-1]


def brownian_migration(pop, cell):
    if pop.size < 100:
        return

    destinations = _livable_destinations(pop.last_copy, cell.last_copy)
    ttl = 0
    for dest in destinations:
        target_pop = util.get_or_create_pop(pop.name, dest.next_copy)
        amount = round(pop.size * 0.001) if pop.size > 1000 else 1
        ttl += amount

        pop.size -= amount
        target_pop.size += amount

    Logger.debug(f"{_log_name}: {ttl} {pop.name} from "
                 f"({cell.x},{cell.y}) did brownian migration "
                 f"to {len(destinations)}")

def _livable_destinations(pop, cell):
    result = util.get_neighbors_with_free_res(
        pop.looks_for[0],
        _all_destinations(pop, cell)
    )
    return result


def migrate(pop, cell):
    """
    Migrate pop living in cell.
    """

    cells_and_pops = []
    for neighbor in _all_destinations(pop.last_copy, cell.last_copy):
        target_pop = neighbor.get_pop(pop.name)
        # чтобы оценить привлекательность, принимаем во внимание
        # только популяции возраста более 0; для 0 еще ни разу
        # не вычислены потребности, поэтому непонятно какая ситуация
        if target_pop and target_pop.age > 0:
            cells_and_pops.append((neighbor, target_pop))

    ttl = 0

    for cell, old_target in cells_and_pops:
        draw = calculate_draw(pop.last_copy, old_target)
        barrier = calculate_barrier(pop.last_copy, old_target, cell.last_copy)

        ttl += _move_amount(pop, old_target.next_copy, draw, barrier)

        for res in pop.last_copy.owned_resources:
            if res.next_copy is None:
                continue

            target_res = old_target.next_copy.get_resource(res.name)

            if not target_res:
                new_res = util.factory.new_resource(res.name, cell)
                agents.set_ownership(old_target.next_copy, new_res)
                target_res = new_res

            _move_amount(res.next_copy, target_res, draw, barrier)

    Logger.debug(f"{_log_name}: {ttl} {pop.name} from ({cell.x},{cell.y}) migrated "
                 f"to {len(cells_and_pops)} neighbors")


def _all_destinations(pop, cell):
    return cell.neighbors


def calculate_draw(pop, target_pop):
    result = target_pop.get_fulfilment() - pop.get_fulfilment()
    return result


def calculate_barrier(pop, target_pop, target_cell):
    return pop.mobility


def _move_amount(entity, target, draw, barrier):
    amount = round(entity.last_copy.size * draw * barrier)
    entity.size -= amount
    target.size += amount
    return amount
