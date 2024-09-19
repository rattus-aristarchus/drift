"""
Общее правило: все чтения состояния должны производиться из
состояния предшествующего хода, запись состояния делается
в текущий ход. Таким образом, последовательность выполнения
эффектов в данном ходу не влияет на результат.
"""

import math

from src.logic.buffers import GridBuffer


def climate(history, grid_buffer: GridBuffer):
    age = grid_buffer.grid.state.age
    mean = history.world.mean_temp

    temp = mean + math.sin(age / 5) / 2
    grid_buffer.grid.state.temperature = temp
    grid_buffer.temp_deviation = history.world.mean_temp - temp
