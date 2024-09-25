# TODO: both these buffers obviously need to be re-written, the calculations shouldn't be hard-coded


class GridBuffer:

    def __init__(self, grid, old_grid, history):
        self.grid = grid
        self.old_grid = old_grid
        self.history = history

        self.temp_deviation = 0

     #   self.all_sootnomads = sum_for_cells('soot_nomads', old_grid.cells_as_list())


class CellBuffer:

    def __init__(self, cell, grid_buffer=None):
        self.cell = cell
