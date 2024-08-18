import csv
import dataclasses
import os
import ast
from typing import List
import yaml
from kivy import Logger

from src.gui.assets import Assets
from src.gui.map_filter import MapFilter
from src.logic.models import ModelStorage, PopModel, BiomeModel, StructureModel, WorldModel, EffectModel, GridModel, \
    CellModel, ResourceModel, NeedModel, Model

# the following methods are required to load effects into models
get_effect = None


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
                    and field.metadata['type'] == "model_list"
            ):
                _replace_ids_with_links(model, field.name, all_models)

    return all_models


def _find_model(model_id, all_models):
    for model in all_models:
        if model.id == model_id:
            return model
    return None


def _replace_ids_with_links(model, field_name, all_models):
    link_list = getattr(model, field_name)
    model_list = []
    for link in link_list:
        link_model = _find_model(link, all_models)
        if link_model:
            model_list.append(link_model)
        else:
            Logger.error(f"Model {model.id} has a bad link: {link}")
    setattr(model, field_name, model_list)


def make_model_storage(models):
    """
    Generate a model storage object with models sorted into categories.
    """

    result = ModelStorage()

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
                result.extend(load_models_from_yaml(file_path))
         #   загружать .csv наверное лучше когда все остальное уже
         #   загружено. либо переписать файл загрузки из csv так чтобы
         #   создавались модели, в которых ссылки можно было бы заменить
         #   по общему механизму
         #
         #   elif ext == ".csv":
         #       result.extend(load_map_model_from_csv(file_path))

    return result


def load_models_from_yaml(path):
    """
    Load models from a single YAML file.
    """
    result = yaml.safe_load(open(path, "r", encoding="utf-8"))
    return result


def load_map_model_from_csv(path):
    """
    Load the model of a map from a CSV file.
    """
    result = []
    return result


def load_models(entities_dir, worlds_dir, maps_dir):

    # load all the stuff
    biomes, pops, structures, resources = _load_dicts_from_yaml(entities_dir)
    worlds = _load_worlds(worlds_dir)

    # now, create models
    result = _create_models_and_put_in_storage(resources=resources,
                                               pops=pops,
                                               biomes=biomes,
                                               structures=structures,
                                               worlds=worlds)

    _update_model_links(result)

    # load maps

    maps = _load_maps(maps_dir, result)
    result.maps = maps

    # replace effect names with effect functions from effect modules

    _replace_effects(result.pops, get_effect)
    _replace_effects(result.structures, get_effect)
    _replace_effects(result.biomes, get_effect)
    _replace_effects(result.worlds, get_effect)
    _replace_effects(result.resources, get_effect)
    _replace_maps(result.worlds, maps)

    return result


def _load_dicts_from_yaml(entities_dir):
    biomes = yaml.safe_load(open(entities_dir + "/biomes.yml", "r", encoding="utf-8"))
    if not biomes:
        biomes = {}
    pops = yaml.safe_load(open(entities_dir + "/pops.yml", "r", encoding="utf-8"))
    if not pops:
        pops = {}
    structures = yaml.safe_load(open(entities_dir + "/structures.yml", "r", encoding="utf-8"))
    if not structures:
        structures = {}
    resources = yaml.safe_load(open(entities_dir + "/resources.yml", "r", encoding="utf-8"))
    if not resources:
        resources = {}
    return biomes, pops, structures, resources


def _load_worlds(worlds_dir):
    worlds = {}

    for element in os.listdir(worlds_dir):
        element_path = os.path.join(worlds_dir, element)
        if os.path.isfile(element_path) and os.path.splitext(element)[1] == ".yml":
            world = yaml.safe_load(open(element_path, "r", encoding="utf-8"))
            world_name = os.path.splitext(element)[0]
            worlds[world_name] = world

    return worlds


def _create_models_and_put_in_storage(resources,
                                      pops,
                                      structures,
                                      biomes,
                                      worlds):
    result = ModelStorage()
    for name, content in resources.items():
        model = ResourceModel(**content)
        result.resources.append(model)

    for name, content in pops.items():
        model = PopModel(**content)
        result.pops.append(model)

    for name, content in structures.items():
        model = StructureModel(**content)
        result.structures.append(model)

    for name, content in biomes.items():
        model = BiomeModel(**content)
        result.biomes.append(model)

    for name, content in worlds.items():
        model = WorldModel(**content)
        model.id = name
        result.worlds.append(model)

    return result


def _update_model_links(model_storage: ModelStorage):
    """
    Ссылки на другие модели лежат в yaml-файлах в качестве
    тупо строк. Эти строки надо заменить правльиными ссылками.
    """
    for pop_model in model_storage.pops:
        outputs = []
        for res_name in pop_model.produces:
            output = model_storage.get_res(res_name)
            _check(output, pop_model.id, res_name)
            outputs.append(output)
        pop_model.produces = outputs

        sells = []
        for res_name in pop_model.sells:
            sell_model = model_storage.get_res(res_name)
            _check(sell_model, pop_model.id, res_name)
            sells.append(sell_model)
        pop_model.sells = sells

        needs = []
        for need_dict in pop_model.needs:
            need = NeedModel(**need_dict)
            need.resource = model_storage.get_res(need.resource)
            needs.append(need)
        pop_model.needs = needs

    for biome_model in model_storage.biomes:
        resources = []
        for res_list in biome_model.resources:
            res_model = model_storage.get_res(res_list[0])
            size = res_list[1]
            resources.append((res_model, size))
        biome_model.resources = resources

    for resource_model in model_storage.resources:
        inputs = []
        for input_name in resource_model.inputs:
            input = model_storage.get_res(input_name)
            _check(input, resource_model.id, input_name)
            inputs.append(input)
        resource_model.inputs = inputs


def _check(to_check, model_name, bad_name):
    if to_check is None:
        Logger.error(f"Model {model_name} has a bad link: {bad_name}")


def _load_maps(maps_dir, model_storage):
    maps = []
    for file in os.listdir(maps_dir):
        file_path = os.path.join(maps_dir, file)
        if os.path.isfile(file_path) and os.path.splitext(file)[1] == ".csv":
            maps.append(_load_map_from_tiled(file_path, model_storage))

    return maps


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
