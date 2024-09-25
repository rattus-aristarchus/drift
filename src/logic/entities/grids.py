import dataclasses
from dataclasses import field
from kivy import Logger

from src.logic.entities.basic import custom_fields, recurrents

from src.logic.buffers import CellBuffer
from src.logic.entities import cells
from src.logic.entities.basic.entities import Entity
from src.logic.entities.basic.recurrents import Recurrent


@dataclasses.dataclass
class GridState(Entity):

    age: int = 0
    temperature: int = 0


@dataclasses.dataclass
class Grid(Entity, Recurrent):
    """
    Карта по состоянию на определенную итерацию модели.
    """

    # клетки представлены словарём словарей, чтобы
    # к ним можно было обращаться cells[x][y]
    cells: dict = field(default_factory=lambda: {})

    # клетки "под наблюдением" - те, по которым мы
    # выводим временные ряды в csv, чтобы их потом
    # можно было отображать на графике
    watched_cells: list = custom_fields.relations_list()
    structures: list = custom_fields.relations_list()
    state: GridState = field(default_factory=lambda: GridState())

    @property
    def width(self):
        return len(self.cells)

    @property
    def height(self):
        if len(self.cells) > 0:
            return len(self.cells[0])
        else:
            return 0

    def cells_as_list(self):
        result = []
        for column in self.cells.values():
            result += column.values()
        return result

    def on_copy(self, original, all_recurrents):
        for x in range(0, original.width):
            self.cells[x] = {}
            for y in range(0, original.height):
                new_cell, all_recurrents = recurrents.copy_recurrent_and_add_to_list(
                    original.cells[x][y],
                    all_recurrents
                )
                # new_cell = cells.copy_cell_without_structures(original.cells[x][y])
                self.cells[x][y] = new_cell
        return all_recurrents

    def do_effects(self, grid_buffer):

        for structure in self.structures:
            structure.do_effects(grid_buffer=grid_buffer)

        for cell in self.cells_as_list():
            cell_buffer = CellBuffer(cell, grid_buffer)

            # this is the main call that calls do_effects for all agents in a cell
            cell.do_effects(cell_buffer, grid_buffer)

            # remove pops that have died out
            to_remove = []
            for pop in cell.pops:
                if pop.size <= 0:
                    to_remove.append(pop)
            for pop in to_remove:
                cell.pops.remove(pop)

            # remove resources that have been emptied out
            to_remove = []
            for res in cell.resources:
                if res.size <= 0:
                    to_remove.append(res)
            for res in to_remove:
                cell.resources.remove(res)


def create_grid_with_default_biome(width, height, biome_name: str, factory, age=0):
    result = Grid()
    result.state = GridState(age=age)

    for x in range(0, width):
        result.cells[x] = {}
        for y in range(0, height):
            result.cells[x][y] = cells.create_cell(x, y, biome_name, factory)

    return result


def increase_age_for_everything(grid, value=1):
    grid.state.age += 1
    for x in range(0, grid.width):
        for y in range(0, grid.height):
            cells.increase_age_for_everything(grid.cells[x][y], value)


def set_neighbors_for_cells(grid):
    for x in range(0, grid.width):
        for y in range(0, grid.height):
            neighbors = _get_neighbors(x, y, grid)
            grid.cells[x][y].neighbors = neighbors


def _get_neighbors(x, y, grid):
    result = []

    x_range = [x - 1, x, x + 1]
    y_range = [y - 1, y, y + 1]

    for poss_x in x_range:
        for poss_y in y_range:
            if poss_x == x and poss_y == y:
                continue
            if poss_x < 0 or poss_x >= grid.width:
                continue
            if poss_y < 0 or poss_y >= grid.height:
                continue
            result.append(grid.cells[poss_x][poss_y])

    return result
