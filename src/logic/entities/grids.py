import dataclasses
import ast
from kivy import Logger
from src.logic.entities import cells
from src.logic.entities.cells import Cell
from src.logic.models import GridModel, ModelStorage, CellModel


def create_grid(width, height, default_biome, age=0):
    result = Grid(width, height)
    result.state = GridState(age=age)

    for x in range(0, result.width):
        result.cells[x] = {}
        for y in range(0, result.height):
            result.cells[x][y] = cells.create_cell(x, y, default_biome)

    return result


def create_grid_from_model(grid_model: GridModel, model_base: ModelStorage, age=0):
    height = len(grid_model.cell_matrix[0])
    width = len(grid_model.cell_matrix)
    result = Grid(width, height)
    result.state = GridState(age=age)

    for x in range(0, width):
        result.cells[x] = {}
        for y in range(0, height):
            cell_model = grid_model.cell_matrix[x][y]
            result.cells[x][y] = create_cell_from_model(cell_model)

    return result


def create_cell_from_dict(x, y, cell_data, model_base: ModelStorage):
    result = None
    if "biome" in cell_data:
        biome_model = model_base.get_biome(cell_data["biome"])
        if biome_model is not None:
            result = cells.create_cell(x, y, biome_model)
        else:
            Logger.error(f"bad biome name '{cell_data["biome"]}' for cell ({x}, {y})")

    # TODO
    if "pops" in cell_data:
        pass

    # TODO
    if "groups" in cell_data:
        pass

    return result


def create_cell_from_model(model: CellModel):
    result = None
    if model.biome:
        result = cells.create_cell(model.x, model.y, model.biome)

    # TODO
    if len(model.pops) > 0:
        pass

    # TODO
    if len(model.groups) > 0:
        pass

    return result


def copy(grid):
    result = Grid(grid.width,
                  grid.height,
                  old_grid=grid)
    result.state = dataclasses.replace(grid.state)

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


@dataclasses.dataclass
class GridState:

    age: int = 0
    temperature: int = 0
