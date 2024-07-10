from src.data import cells
from src.data.cells import Cell


def populate(grid, old_grid=None):
    for x in range(0, grid.width):
        grid.cells[x] = {}
        for y in range(0, grid.height):
            if old_grid is None:
                new_cell = Cell(x, y)
            else:
                new_cell = cells.copy_cell(old_grid.cells[x][y])
                cells.increase_age(new_cell)
            grid.cells[x][y] = new_cell

    if old_grid is not None:
        for watched_cell in old_grid.watched_cells:
            grid.watched_cells.append(grid.cells[watched_cell.x][watched_cell.y])


def copy(grid):
    new_grid = Grid(grid.width,
                    grid.height,
                    old_grid=grid)
    populate(new_grid, grid)
    return new_grid


def increase_age(grid, value=1):
    for x in range(0, grid.width):
        for y in range(0, grid.height):
            cells.increase_age(grid.cells[x][y], value)


class Grid:

    def __init__(self, width, height, old_grid=None):
        self.width = width
        self.height = height
        #dict of dicts
        self.cells = {}
        self.watched_cells = []

        self.state = GridState()

    def cells_as_list(self):
        result = []
        for column in self.cells.values():
            result += column.values()
        return result


class GridState:

    def __init__(self):
        self.temperature = 0
