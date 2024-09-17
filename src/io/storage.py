import csv
import dataclasses
import os
import ast
from typing import List
import yaml
from kivy import Logger

from src.gui.assets import Assets
from src.gui.map_filter import MapFilter
from src.io import load_factory, load_worlds
from src.logic.models.models import PopModel, BiomeModel, StructureModel, WorldModel, EffectModel, \
    CellModel, ResourceModel, NeedModel, Model
from src.logic.models.model_base import ModelBase


# the following methods are required to load effects into models
get_effect = None


def load_assets(assets_dir):
    """
    Читаем с диска всё, необходимое для графики.
    """
    colors = yaml.safe_load(open(assets_dir + "/palette.yml", "r", encoding="utf-8"))
    images = yaml.safe_load(open(assets_dir + "/images.yml", "r", encoding="utf-8"))
    map_filter_data = yaml.safe_load(open(assets_dir + "/map_filters.yml", "r", encoding="utf-8"))
    map_filters = []
    for id, data in map_filter_data.items():
        map_filters.append(MapFilter(**data))

    result = Assets(colors=colors, images=images, map_filters=map_filters)
    return result


def load_entities(worlds_dir):
    all_models = load_models(worlds_dir)
    factory = load_factory.make_factory_from_models(all_models)
    worlds = load_worlds.create_worlds(all_models)
    load_worlds.load_maps_into_worlds(worlds, worlds_dir, factory)
    return factory, worlds


def load_models(worlds_dir):
    all_models = []
    all_models.extend(_load_all_models(worlds_dir))

    effect_models = []
    for model in all_models:
        if isinstance(model, EffectModel):
            effect_models.append(model)

    # заменяем названия эффектов ссылками на них
    _replace_effects(effect_models, get_effect)
    return all_models


def make_model_base(worlds_dir):
    """
    Читаем с диска все прототипы сущностей
    """

    all_models = []
    all_models.extend(_load_all_models(worlds_dir))
    _sort_model_links(all_models)
    model_base = _make_base_from_models(all_models)
    model_base.maps = _load_all_maps(worlds_dir, model_base)
    _replace_maps(model_base.worlds, model_base.maps)
    return model_base


def _sort_model_links(all_models):
    """
    For models that refer to other models or to effects, replace
    string pointers
    with actual links.
    """

    # вначале разбираемся с эффектами. отбираем только те модели, у
    # которых могут быть эффекты
    effect_models = []
    for model in all_models:
        if isinstance(model, EffectModel):
            effect_models.append(model)

    # заменяем названия эффектов ссылками на них
    _replace_effects(effect_models, get_effect)

    # теперь заменяем названия моделей ссылками на модели
    for model in all_models:
        _class = type(model)

        # вся эта ерунда работает только для dataclass
        if not dataclasses.is_dataclass(model):
            raise Exception(f"A list of models contains object of type "
                            f"{_class} that isn't a dataclass")

        # заменять названия ссылками нужно только у специально
        # обозначенных нами полей. обходим все поля класса и для
        # нужных производим замену строк на ссылки
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


def _find_model(model_name, all_models):
    for model in all_models:
        if model.name == model_name:
            return model
    return None


def _replace_ids_with_links_in_list(model, field_name, all_models):
    """
    В поле field_name модели model, являющемся списком, заменяем
    все строки ссылками на модели. Модели ищем в списке all_models
    """
    link_list = getattr(model, field_name)
    model_list = []
    for link in link_list:
        link_model = _find_model(link, all_models)
        if link_model:
            model_list.append(link_model)
        else:
            Logger.error(f"Model {model.name} has a bad link: {link}")
    setattr(model, field_name, model_list)


def _replace_ids_with_links_in_list_list(model, field_name, all_models):
    """
    В поле field_name модели model, являющемся списком списков, заменяем
    все строки ссылками на модели. Модели ищем в списке all_models
    """
    list_list = getattr(model, field_name)
    new_list_list = []

    for sub_list in list_list:
        new_sub_list = sub_list.copy()
        link_model = _find_model(new_sub_list[0], all_models)
        if link_model:
            new_sub_list[0] = link_model
        else:
            Logger.error(f"Model {model.name} has a bad link: {new_sub_list[0]}")
        new_list_list.append(new_sub_list)

    setattr(model, field_name, new_list_list)

"""
def _make_base_from_models(models):
  
 #   Generate a model storage object with models sorted into categories.
  
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
"""

def _load_all_models(path):
    """
    Walk the directory recursively and load models from all files in it.
    """
    result = []

    for root, dirs, files in os.walk(path):
        for file in files:
            ext = os.path.splitext(file)[1]
            file_path = os.path.join(root, file)
            if ext == ".yml" or ext == ".yaml":
                new_models = _load_models_from_yaml_file(file_path)
                result.extend(new_models)

    return result


def _load_models_from_yaml_file(path):
    """
    Load models from a single YAML file.
    """
    result = yaml.safe_load(open(path, "r", encoding="utf-8"))
    if not result:
        result = []
    return result


def _replace_effects(model_list: List[EffectModel], get_effect):
    """
    Заменяем названия эффектов в поле model.effects ссылками на эффекты
    """
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
