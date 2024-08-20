import csv
import dataclasses
import os
import ast
from typing import List
import yaml
from kivy import Logger

from src.gui.assets import Assets
from src.gui.map_filter import MapFilter
from src.logic.models.models import PopModel, BiomeModel, StructureModel, WorldModel, EffectModel, GridModel, \
    CellModel, ResourceModel, NeedModel, Model
from src.logic.models.model_base import ModelBase


# the following methods are required to load effects into models
get_effect = None


def make_model_base(entities_dir, worlds_dir, maps_dir):
    all_models = []
    all_models.extend(load_all_models(entities_dir))
    all_models.extend(load_all_models(worlds_dir))
    sort_model_links(all_models)
    model_base = make_base_from_models(all_models)
    model_base.maps = load_all_maps(maps_dir, model_base)
    _replace_maps(model_base.worlds, model_base.maps)
    return model_base


def sort_model_links(all_models):
    """
    For models that refer to other models, replace string pointers
    with actual links.
    """

    effect_models = []
    for model in all_models:
        if isinstance(model, EffectModel):
            effect_models.append(model)

    _replace_effects(effect_models, get_effect)

    for model in all_models:
        # обходим поля класса, для каждого поля получаем его значение
        _class = type(model)
        for field in dataclasses.fields(_class):
            if (
                    field.metadata
                    and 'type' in field.metadata.keys()
            ):
                if field.metadata['type'] == "model_list":
                    _replace_ids_with_links_in_list(model, field.name, all_models)
                elif field.metadata['type'] == "model_list_list":
                    _replace_ids_with_links_in_list_list(model, field.name, all_models)

    return all_models


def _find_model(model_id, all_models):
    for model in all_models:
        if model.id == model_id:
            return model
    return None


def _replace_ids_with_links_in_list(model, field_name, all_models):
    link_list = getattr(model, field_name)
    model_list = []
    for link in link_list:
        link_model = _find_model(link, all_models)
        if link_model:
            model_list.append(link_model)
        else:
            Logger.error(f"Model {model.id} has a bad link: {link}")
    setattr(model, field_name, model_list)


def _replace_ids_with_links_in_list_list(model, field_name, all_models):
    list_list = getattr(model, field_name)
    new_list_list = []

    for sub_list in list_list:
        new_sub_list = sub_list.copy()
        link_model = _find_model(new_sub_list[0], all_models)
        if link_model:
            new_sub_list[0] = link_model
        else:
            Logger.error(f"Model {model.id} has a bad link: {new_sub_list[0]}")
        new_list_list.append(new_sub_list)

    setattr(model, field_name, new_list_list)


def make_base_from_models(models):
    """
    Generate a model storage object with models sorted into categories.
    """

    result = ModelBase()

    for model in models:
        if isinstance(model, PopModel):
            result.pops.append(model)
        elif isinstance(model, StructureModel):
            result.structures.append(model)
        elif isinstance(model, ResourceModel):
            result.resources.append(model)
        elif isinstance(model, BiomeModel):
            result.biomes.append(model)
        elif isinstance(model, GridModel):
            result.maps.append(model)
        elif isinstance(model, WorldModel):
            result.worlds.append(model)

    return result


def load_all_models(path):
    """
    Walk the directory recursively and load models from all files in it.
    """
    result = []

    for root, dirs, files in os.walk(path):
        for file in files:
            ext = os.path.splitext(file)[1]
            file_path = os.path.join(root, file)
            if ext == ".yml" or ext == ".yaml":
                new_models = load_models_from_yaml(file_path)
                result.extend(new_models)

    return result


def load_models_from_yaml(path):
    """
    Load models from a single YAML file.
    """
    result = yaml.safe_load(open(path, "r", encoding="utf-8"))
    if not result:
        result = []
    return result


def load_all_maps(path, model_base):
    """
    Walk the directory recursively and load map models from all files in it.
    """
    result = []

    for root, dirs, files in os.walk(path):
        for file in files:
            ext = os.path.splitext(file)[1]
            file_path = os.path.join(root, file)
            if ext == ".csv":
                map_model = _load_map_from_tiled(file_path, model_base)
                result.append(map_model)

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
#        if model.effects is None:
 #           model.effects = []
  #      else:
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


def _load_map_from_tiled(path, model_base):
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
                biome = model_base.get_biome(cell_string)
                if biome is None:
                    Logger.error(f"Map file at {path} contains an invalid biome name: {cell_string}")
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
