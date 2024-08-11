import dataclasses
from dataclasses import field
from kivy import Logger

from src.logic.entities.basic import recurrents
import src.logic.entities.agents.structures
from src.logic.buffers import CellBuffer
from src.logic.entities import cells
from src.logic.entities.basic.entities import Entity
from src.logic.entities.basic.recurrents import Recurrent
from src.logic.models import GridModel, ModelStorage, CellModel


@dataclasses.dataclass
class GridState(Entity):

    age: int = 0
    temperature: int = 0


@dataclasses.dataclass
class Grid(Entity, Recurrent):
    """
    Карта по состоянию на определенную итерацию модели.
    """

    width: int = 0
    height: int = 0
        # клетки представлены словарём словарей, чтобы
        # к ним можно было обращаться cells[x][y]
    cells: dict = field(default_factory=lambda: {})
        # клетки "под наблюдением" - те, по которым мы
        # выводим временные ряды в csv, чтобы их потом
        # можно было отображать на графике
    watched_cells: list = src.logic.entities.basic.recurrents.relations_list() # list = field(default_factory=lambda: [])
    structures: list = src.logic.entities.basic.recurrents.relations_list() # list = field(default_factory=lambda: [])
    state: GridState = None

    def cells_as_list(self):
        result = []
        for column in self.cells.values():
            result += column.values()
        return result

    def on_copy(self, original, all_recurrents):
        for x in range(0, self.width):
            self.cells[x] = {}
            for y in range(0, self.height):
                new_cell, all_recurrents = src.logic.entities.basic.recurrents.copy_recurrent_and_add_to_list(
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


def create_grid(width, height, default_biome, age=0):
    result = Grid(width=width, height=height)
    result.state = GridState(age=age)

    for x in range(0, result.width):
        result.cells[x] = {}
        for y in range(0, result.height):
            result.cells[x][y] = cells.create_cell(x, y, default_biome)

    return result


def create_grid_from_model(grid_model: GridModel, model_base: ModelStorage, age=0):
    height = len(grid_model.cell_matrix[0])
    width = len(grid_model.cell_matrix)
    result = Grid(
        width=width,
        height=height
    )
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
    if "resources" in cell_data:
        pass

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
    if len(model.resources) > 0:
        pass

    # TODO
    if len(model.pops) > 0:
        pass

    # TODO
    if len(model.groups) > 0:
        pass

    return result


def increase_age(grid, value=1):
    grid.state.age += 1
    for x in range(0, grid.width):
        for y in range(0, grid.height):
            cells.increase_age(grid.cells[x][y], value)
