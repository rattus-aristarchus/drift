import csv
import os
from kivy import Logger

from src.logic.entities import cells
from src.logic.entities.cells import Cell
from src.logic.entities.grids import Grid
from src.io import models
from src.io.models import WorldModel


def create_worlds(all_models):
    result = []
    for model in all_models:
        if isinstance(model, WorldModel):
            world = models.create_from_model(model)
            result.append(world)
    return result


def load_maps_into_worlds(worlds, worlds_dir, factory):
    maps = _load_all_maps(worlds_dir, factory)
    _replace_maps(worlds, maps)


def _load_all_maps(path, factory):
    """
    Walk the directory recursively and load map models from all files in it.
    """
    result = []

    for root, dirs, files in os.walk(path):
        for file in files:
            ext = os.path.splitext(file)[1]
            file_path = os.path.join(root, file)
            if ext == ".csv":
                map_model = _load_map_from_tiled(file_path, factory)
                result.append(map_model)

    return result


def _load_map_from_tiled(path, factory):
    result = None
    with open(path) as csv_file:
        name = os.path.splitext(os.path.basename(path))[0]
        result = Grid(name=name)

        csvreader = csv.reader(csv_file, delimiter=',')
        cell_rows = []
        x = 0
        y = 0
        for row in csvreader:
            cell_row = []
            for cell_string in row:
                cell = cells.create_cell(x, y, cell_string, factory)
                cell_row.append(cell)
                x += 1
            cell_rows.append(cell_row)
            y += 1
            x = 0

        # the csv reader reads the file by rows; however, we
        # need to arrange them by columns first, so that we
        # can call matrix[x][y] (x being the index of a column)

        for x in range(0, len(cell_rows[0])):
            result.cells[x] = {}
            for y in range(0, len(cell_rows)):
                result.cells[x][y] = cell_rows[y][x]

        result.width = len(result.cells)
        if result.width > 0:
            result.height = len(result.cells[0])
        else:
            result.height = 0

    return result

"""
def _load_map(path, model_storage):
    result = None
    with open(path) as csv_file:
        name = os.path.splitext(os.path.basename(path))[0]
        result = GridModel(id=name)

        csvreader = csv.reader(csv_file, delimiter=';')
        rows = []
        for row in csvreader:
            cell_row = []
            for cell in row:
                cell_row.append(cell)
            rows.append(cell_row)

        # the csv reader reads the file by rows; however, we
        # need to arrange them by columns first, so that we
        # can call matrix[x][y] (x being the index of a column)

        for x in range(0, len(rows[0])):
            column = []
            for y in range(0, len(rows)):
                column.append(rows[y][x])
            result.cell_matrix.append(column)

    return result
"""

def _replace_maps(worlds, maps):
    for world in worlds:
        for map in maps:
            if world.map == map.name:
                world.map = map
