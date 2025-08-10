"""
Общее правило: все чтения состояния должны производиться из
состояния предшествующего хода, запись состояния делается
в текущий ход. Таким образом, последовательность выполнения
эффектов в данном ходу не влияет на результат.
"""

import math


def climate(grid_write, grid_read, buffer):
    age = grid_read.state.age
    mean = buffer.world.mean_temp

    temp = mean + math.sin(age + 1 / 5) / 2
    grid_write.state.temperature = temp
    buffer.memory["temp_deviation"] = buffer.world.mean_temp - temp
