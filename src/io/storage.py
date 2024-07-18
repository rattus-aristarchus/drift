import csv
import os
import sys
from typing import List
import yaml
from kivy import Logger

from src.gui.assets import Assets
from src.gui.map_filter import MapFilter
from src.logic.models import ModelStorage, PopModel, BiomeModel, GroupModel, WorldModel, EffectModel, GridModel, \
    CellModel

# the following methods are required to load effects into models
get_pop_effect = None
get_group_effect = None
get_biome_effect = None
get_world_effect = None


def load_models(entities_dir, worlds_dir, maps_dir):

    # load all the stuff

    biomes = yaml.safe_load(open(entities_dir + "/biomes.yml", "r", encoding="utf-8"))
    pops = yaml.safe_load(open(entities_dir + "/pops.yml", "r", encoding="utf-8"))
    groups = yaml.safe_load(open(entities_dir + "/groups.yml", "r", encoding="utf-8"))

    worlds = {}

    for element in os.listdir(worlds_dir):
        element_path = os.path.join(worlds_dir, element)
        if os.path.isfile(element_path) and os.path.splitext(element)[1] == ".yml":
            world = yaml.safe_load(open(element_path, "r", encoding="utf-8"))
            world_name = os.path.splitext(element)[0]
            worlds[world_name] = world

    # now, create models

    result = ModelStorage()
    for name, content in pops.items():
        model = PopModel(**content)
        result.pops.append(model)

    for name, content in groups.items():
        model = GroupModel(**content)
        result.groups.append(model)

    for name, content in biomes.items():
        model = BiomeModel(**content)
        result.biomes.append(model)

    for name, content in worlds.items():
        model = WorldModel(**content)
        model.id = name
        result.worlds.append(model)

    # load maps

    maps = []
    for file in os.listdir(maps_dir):
        file_path = os.path.join(maps_dir, file)
        if os.path.isfile(file_path) and os.path.splitext(file)[1] == ".csv":
            maps.append(_load_map_from_tiled(file_path, result))
    result.maps = maps

    # replace effect names with effect functions from effect modules

    _replace_effects(result.pops, get_pop_effect)
    _replace_effects(result.groups, get_group_effect)
    _replace_effects(result.biomes, get_biome_effect)
    _replace_effects(result.worlds, get_world_effect)
    _replace_maps(result.worlds, maps)

    return result


def load_assets(assets_dir):
    colors = yaml.safe_load(open(assets_dir + "/palette.yml", "r", encoding="utf-8"))
    images = yaml.safe_load(open(assets_dir + "/images.yml", "r", encoding="utf-8"))
    map_filter_data = yaml.safe_load(open(assets_dir + "/map_filters.yml", "r", encoding="utf-8"))
    map_filters = []
    for id, data in map_filter_data.items():
        map_filters.append(MapFilter(**data))

    result = Assets(colors=colors, images=images, map_filters=map_filters)
    return result


def _replace_maps(worlds, maps):
    for world in worlds:
        for map in maps:
            if world.map == map.id:
                world.map = map


def _replace_effects(model_list: List[EffectModel], get_effect):
    for model in model_list:
        if model.effects is None:
            model.effects = []
        else:
            model.effects = _get_model_effects(model, get_effect)


def _get_model_effects(model: EffectModel, get_effect):
    result = []
    for effect_name in model.effects:
        result.append(get_effect(effect_name))
    return result


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


def _load_map_from_tiled(path, model_storage):
    result = None
    with open(path) as csv_file:
        name = os.path.splitext(os.path.basename(path))[0]
        result = GridModel(id=name)

        csvreader = csv.reader(csv_file, delimiter=',')
        cell_rows = []
        x = 0
        y = 0
        for row in csvreader:
            cell_row = []
            for cell_string in row:
                cell = CellModel(x=x, y=y)
                biome = model_storage.get_biome(cell_string)
                if biome is None:
                    Logger.error(f"Map file at {path} conatins an invalid biome name: {cell_string}")
                else:
                    cell.biome = biome
                cell_row.append(cell)
                x += 1
            cell_rows.append(cell_row)
            y += 1
            x = 0

        # the csv reader reads the file by rows; however, we
        # need to arrange them by columns first, so that we
        # can call matrix[x][y] (x being the index of a column)

        for x in range(0, len(cell_rows[0])):
            column = []
            for y in range(0, len(cell_rows)):
                column.append(cell_rows[y][x])
            result.cell_matrix.append(column)

    return result
