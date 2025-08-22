from src.logic.effects import effects_util
from src.logic.entities.agents import ownership
from kivy import Logger

_log_name = __name__.split('.')[-1]


def brownian_migration(pop_write, pop_read, cell_write, cell_read):
    """
    Случайное бродяжничество. Так создаются популяции в новых клетках.
    """
    if pop_read.size < 100:
        return

    old_destinations = _livable_destinations(pop_read, cell_read)
    ttl = 0
    amount = round(pop_read.size * 0.001) if pop_read.size > 1000 else 1
    for old_dest in old_destinations:
        target_write = effects_util.get_or_create_pop(pop_read.name, old_dest.next_copy)
        ttl += amount

        pop_write.size -= amount
        target_write.size += amount

        fraction = amount / pop_read.size
        for res_read in pop_read.owned_resources:
            _migrate_property(
                res_read,
                res_read.next_copy,
                pop_write,
                target_write,
                old_dest.next_copy,
                fraction
            )

    Logger.debug(f"{_log_name}: {ttl} {pop_read.name} from "
                 f"({cell_read.x},{cell_read.y}) did brownian migration "
                 f"to {len(old_destinations)} neighbors")


def _livable_destinations(pop, cell):
    result = effects_util.get_neighbors_with_free_res(
        pop.looks_for[0],
        _all_destinations(cell)
    )
    return result


def migrate(pop_write, pop_read, cell_write, cell_read):
    """
    Рассчитываем миграцию в популяции других клеток для данной популяции.
    """

    # среди возможных целей миграции выбираем те, где есть такие же популяции
    cells_and_pops = []
    for neighbor in _all_destinations(cell_read):
        target_pop = neighbor.get_pop(pop_read.name)
        # чтобы оценить привлекательность, принимаем во внимание
        # только популяции возраста более 0; для 0 еще ни разу
        # не вычислены потребности, поэтому непонятно какая ситуация
        if target_pop and target_pop.age > 0:
            cells_and_pops.append((neighbor, target_pop))

    # для учета, сколько всего мигрировало
    ttl = 0

    for old_cell, old_target in cells_and_pops:
        # рассчитываем привлекательность цели и сложность туда добраться
        draw = _calculate_draw(pop_read, old_target)
        barrier = _calculate_barrier(pop_read, old_target, old_cell)

        # мигрируем
        fraction = draw * barrier
        amount = round(pop_read.size * fraction)
        _move_amount(pop_write, old_target.next_copy, amount)
        ttl += amount

        # вместе с популяцией мигрирует ее собственность
        for res_read in pop_read.owned_resources:
            _migrate_property(
                res_read,
                res_read.next_copy,
                pop_write,
                old_target.next_copy,
                old_cell.next_copy,
                fraction
            )


    Logger.debug(f"{_log_name}: {ttl} {pop_read.name} from ({cell_read.x},{cell_read.y}) migrated "
                 f"to {len(cells_and_pops)} neighbors; {pop_write.size} people are left")


def _migrate_property(res_read, res_write, owner_write, target, cell_write, fraction):
        # ... но только если она 1. не была удалена и 2. движимая
        if res_write is None or not res_read.movable:
            return

        # аналогичный ресурс у целевой популяции
        target_res = target.get_resource(res_read.name)

        # если таковых нет, создаем
        if not target_res:
            target_res = effects_util.factory.new_resource(res_read.name, cell_write)
            ownership.set_ownership(target, target_res)

        # мигрируем
        amount = round(res_read.size * fraction)
        _move_amount(res_write, target_res, amount)

        # обновляем собственность
        ownership.add_ownership(target, target_res, amount)
        ownership.subtract_ownership(owner_write, res_write, amount)


def _all_destinations(cell):
    return cell.neighbors


def _calculate_draw(pop, target_pop):
    """
    Притяжение - от 0 до 1, какая доля исходной популяции готова
    перейти в целевую.
    """
    result = target_pop.get_fulfilment() - pop.get_fulfilment()
    if result < 0:
        result = 0
    return result


def _calculate_barrier(pop, target_pop, target_cell):
    """
    Порог - от 0 до 1, какая доля готовых к переходу
    могут перейти.
    """
    return pop.mobility


def _move_amount(entity, target, amount):
    entity.size -= amount
    target.size += amount
    return amount
