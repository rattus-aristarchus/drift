import os
from typing import List
import yaml

from src.gui.assets import Assets
from src.gui.map_filter import MapFilter
from src.io import load_factory, load_worlds
from src.io.models import AgentModel
from src.logic.entities.agents.agents import Agent

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


def load_namespaces(namespaces_dir):
    """
    Читаем с диска все сущности.

    Каждая папка первого уровня в папке namespaces считается отдельным
    пространством имен;
    для каждой такой папки создается отдельная фабрика (содержащая все сущности
    этой папки), и имена сущностей должны быть уникальны внутри пространства
    имён.

    Это делается для того, чтобы можно было держать в ресурсах разные проекты и
    не париться о том, чтобы имена были уникальными между проектами.
    """

    factories = []
    list_subfolders_with_paths = [f.path for f in os.scandir(namespaces_dir) if f.is_dir()]
    for namespace in list_subfolders_with_paths:
        factory = make_factory_from_namespace(namespace)
        factories.append(factory)
    return factories


def make_factory_from_namespace(namespace):
    all_models = _load_models_and_replace_effects(namespace)
    factory = load_factory.make_factory_from_models(all_models)
    load_worlds.load_maps_into_worlds(list(factory.worlds.values()), namespace, factory)
    return factory


def _load_models_and_replace_effects(worlds_dir):
    all_models = []
    all_models.extend(_load_all_models(worlds_dir))

    effect_models = []
    for model in all_models:
        if isinstance(model, AgentModel):
            effect_models.append(model)

    # заменяем названия эффектов ссылками на них
    _replace_effects(effect_models, get_effect)
    return all_models


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


def _replace_effects(model_list: List[AgentModel], get_effect):
    """
    Заменяем названия эффектов в поле model.effects ссылками на эффекты
    """
    for model in model_list:
        if not hasattr(model, "effects") or model.effects is None:
            model.effects = []
        else:
            model.effects = _get_model_effects(model, get_effect)


def _get_model_effects(model: Agent, get_effect):
    result = []
    for effect_name in model.effects:
        result.append(get_effect(effect_name))
    return result
