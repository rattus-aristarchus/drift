from src.logic.effects.util import sum_for_cells, get_neighbors

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
        if grid_buffer:
            self.neighbors = get_neighbors(cell.x, cell.y, grid_buffer.grid)
            if grid_buffer.old_grid:
                self.old_neighbors = get_neighbors(cell.x, cell.y, grid_buffer.old_grid)

        # self.nomad_capacity = round(get_pop_num('steppe_grass', cell) / 10 - get_pop_num('soot_nomads', cell))
        # self.wheatmen_capacity = round(get_pop_num('wheat', cell) / 2 - get_pop_num('wheatmen', cell))
