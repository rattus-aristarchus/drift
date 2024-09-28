from src.logic.effects import util
from src.logic.entities.agents import ownership
from kivy import Logger

_log_name = __name__.split('.')[-1]


def brownian_migration(pop, cell):
    """
    Случайное бродяжничество. Так создаются популяции в новых клетках.
    """
    if pop.size < 100:
        return

    destinations = _livable_destinations(pop.last_copy, cell.last_copy)
    ttl = 0
    amount = round(pop.size * 0.001) if pop.size > 1000 else 1
    for dest in destinations:
        target_pop = util.get_or_create_pop(pop.name, dest.next_copy)
        ttl += amount

        pop.size -= amount
        target_pop.size += amount

    Logger.debug(f"{_log_name}: {ttl} {pop.name} from "
                 f"({cell.x},{cell.y}) did brownian migration "
                 f"to {len(destinations)} neighbors")


def _livable_destinations(pop, cell):
    result = util.get_neighbors_with_free_res(
        pop.looks_for[0],
        _all_destinations(pop, cell)
    )
    return result


def migrate(pop, cell):
    """
    Рассчитываем миграцию в популяции других клеток для данной популяции.
    """

    # среди возможных целей миграции выбираем те, где есть такие же популяции
    cells_and_pops = []
    for neighbor in _all_destinations(pop.last_copy, cell.last_copy):
        target_pop = neighbor.get_pop(pop.name)
        # чтобы оценить привлекательность, принимаем во внимание
        # только популяции возраста более 0; для 0 еще ни разу
        # не вычислены потребности, поэтому непонятно какая ситуация
        if target_pop and target_pop.age > 0:
            cells_and_pops.append((neighbor, target_pop))

    # для учета, сколько всего мигрировало
    ttl = 0

    for cell, old_target in cells_and_pops:
        # рассчитываем привлекательность цели и сложность туда добраться
        draw = calculate_draw(pop.last_copy, old_target)
        barrier = calculate_barrier(pop.last_copy, old_target, cell.last_copy)

        # мигрируем
        amount = round(pop.last_copy.size * draw * barrier)
        _move_amount(pop, old_target.next_copy, amount)
        ttl += amount

        # вместе с популяцией мигрирует ее собственность
        for old_res in pop.last_copy.owned_resources:
            # ... но только если она 1. не была удалена и 2. движимая
            if old_res.next_copy is None or not old_res.movable:
                continue

            # аналогичный ресурс в целевой клетке
            target_res = old_target.next_copy.get_resource(old_res.name)

            # если таковых нет, создаем
            if not target_res:
                new_res = util.factory.new_resource(old_res.name, cell)
                ownership.set_ownership(old_target.next_copy, new_res)
                target_res = new_res

            # мигрируем
            amount = round(old_res.size * draw * barrier)
            _move_amount(old_res.next_copy, target_res, amount)

    Logger.debug(f"{_log_name}: {ttl} {pop.name} from ({cell.x},{cell.y}) migrated "
                 f"to {len(cells_and_pops)} neighbors")


def _all_destinations(pop, cell):
    return cell.neighbors


def calculate_draw(pop, target_pop):
    """
    Притяжение - от 0 до 1, какая доля исходной популяции готова
    перейти в целевую.
    """
    result = target_pop.get_fulfilment() - pop.get_fulfilment()
    if result < 0:
        result = 0
    return result


def calculate_barrier(pop, target_pop, target_cell):
    """
    Порог - от 0 до 1, какая доля готовых к переходу
    могут перейти.
    """
    return pop.mobility


def _move_amount(entity, target, amount):
    entity.size -= amount
    target.size += amount
    return amount
