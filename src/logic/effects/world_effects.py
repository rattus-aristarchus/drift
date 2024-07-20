import math

from src.logic.buffers import GridBuffer


def get_effect(func_name):
    return eval(func_name)


"""
All world effects accept two parameteres:
- history
- the grid buffer
"""


def climate(history, grid_buffer):
    age = grid_buffer.grid.state.age
    mean = history.world_model.mean_temp

    temp = mean + math.sin(age / 5) / 2
    grid_buffer.grid.state.temperature = temp
