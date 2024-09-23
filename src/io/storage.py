import os
from typing import List
import yaml

from src.gui.assets import Assets
from src.gui.map_filter import MapFilter
from src.io import load_factory, load_worlds, models
from src.io.models import RuleModel, BiomeRuleModel, ResourceRuleModel, PopulationRuleModel
from src.logic.entities.agents.agents import Agent
from src.logic.rules.rulebook import Rules
from src.logic.rules.rules import Rule, BiomeRule, ResourceRule, PopulationRule

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
    all_models = _load_models(worlds_dir)
    factory = load_factory.make_factory_from_models(all_models)
    worlds = load_worlds.create_worlds(all_models)
    load_worlds.load_maps_into_worlds(worlds, worlds_dir, factory)
    rules = _create_rulebook(all_models)
    return factory, worlds, rules


def _load_models(worlds_dir):
    all_models = []
    all_models.extend(_load_all_models(worlds_dir))

    effect_models = []
    for model in all_models:
        if isinstance(model, Agent):
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


def _replace_effects(model_list: List[Agent], get_effect):
    """
    Заменяем названия эффектов в поле model.effects ссылками на эффекты
    """
    for model in model_list:
        if model.effects is None:
            model.effects = []
        else:
            model.effects = _get_model_effects(model, get_effect)


def _get_model_effects(model: Agent, get_effect):
    result = []
    for effect_name in model.effects:
        result.append(get_effect(effect_name))
    return result


def _create_rulebook(all_models):
    result = Rules()
    for model in all_models:
        if isinstance(model, RuleModel):
            rule = models.create_from_model(model)
            if isinstance(rule, BiomeRule):
                result.biomes[rule.name] = rule
            elif isinstance(rule, ResourceRule):
                result.resources[rule.name] = rule
            elif isinstance(rule, PopulationRule):
                result.populations[rule.name] = rule

    return result
