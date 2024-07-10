from src.data import cells


def create_grid(width, height):
    result = Grid(width, height)
    result.state = GridState()

    for x in range(0, result.width):
        result.cells[x] = {}
        for y in range(0, result.height):
            result.cells[x][y] = cells.create_cell(x, y)

    return result


def copy(grid):
    result = Grid(grid.width,
                  grid.height,
                  old_grid=grid)

    for x in range(0, result.width):
        result.cells[x] = {}
        for y in range(0, result.height):
            new_cell = cells.copy_cell(grid.cells[x][y])
            result.cells[x][y] = new_cell

    for watched_cell in grid.watched_cells:
        result.watched_cells.append(
            result.cells[watched_cell.x][watched_cell.y]
        )

    return result


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

        self.state = None

    def cells_as_list(self):
        result = []
        for column in self.cells.values():
            result += column.values()
        return result


class GridState:

    def __init__(self):
        self.temperature = 0
