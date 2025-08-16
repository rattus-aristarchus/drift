"""
Общее правило: все чтения состояния должны производиться из
состояния предшествующего хода, запись состояния делается
в текущий ход. Таким образом, последовательность выполнения
эффектов в данном ходу не влияет на результат.
"""

from src.logic.effects import effects_util


def temp_change(cell_write, cell_read, buffer):
    # if the biome has no capacity, we don't need to change it
    if not cell_write.biome.capacity:
        return

    # first, we have to know, how much temperature deviation is "bad" or "good".
    # we know that from world.deviation_50
    deviation_factor = buffer.memory["temp_deviation"] / buffer.world.deviation_50

    # for a wet climate, high temperature is bad, cold is good - so the
    # deviation factor is accurate; but for a wet climate, hot is bad. so:
    if cell_read.biome.moisture == "dry":
        deviation_factor = -deviation_factor

    # deviation_50 means the capacities have to be reduced/increased by 50%
    # positive deviation_factor - too hot; negative - too cold
    if deviation_factor > 0:
        multiplier = 1 + deviation_factor / (deviation_factor + 1)
    else:
        multiplier = 1 + deviation_factor / (1 - deviation_factor)

    # multiplier is how much the capacities are changed
    for name, mean_cap in cell_read.biome.capacity.items():
        cap = round(mean_cap * multiplier)
        cell_write.biome.capacity[name] = cap

