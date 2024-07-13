from src.data import cells


def create_grid(width, height, default_biome, age=0):
    result = Grid(width, height)
    result.state = GridState()
    result.state.age = age

    for x in range(0, result.width):
        result.cells[x] = {}
        for y in range(0, result.height):
            result.cells[x][y] = cells.create_cell(x, y, default_biome)

    return result


def copy(grid):
    result = Grid(grid.width,
                  grid.height,
                  old_grid=grid)
    result.state = _copy_state(grid.state)

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
    grid.state.age += 1
    for x in range(0, grid.width):
        for y in range(0, grid.height):
            cells.increase_age(grid.cells[x][y], value)


def _copy_state(grid_state):
    result = GridState()
    result.age = grid_state.age
    result.temperature = grid_state.temperature
    return result


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
        self.age = 0
        self.temperature = 0
