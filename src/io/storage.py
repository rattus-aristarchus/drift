import os
import sys
from typing import List
import yaml
from kivy import Logger

from src.gui.assets import Assets
from src.logic.models import ModelStorage, PopModel, BiomeModel, GroupModel, WorldModel, EffectModel


# the following methods are required to load effects into models
get_pop_effect = None
get_group_effect = None
get_biome_effect = None
get_world_effect = None


def load_models(data_dir):

    # load all the stuff

    entities_dir = os.path.join(data_dir, "entities")
    biomes = yaml.safe_load(open(entities_dir + "/biomes.yml", "r", encoding="utf-8"))
    pops = yaml.safe_load(open(entities_dir + "/pops.yml", "r", encoding="utf-8"))
    groups = yaml.safe_load(open(entities_dir + "/groups.yml", "r", encoding="utf-8"))

    worlds_dir = os.path.join(data_dir, "worlds")
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

    # replace effect names with effect functions from effect modules

    _replace_effects(result.pops, get_pop_effect)
    _replace_effects(result.groups, get_group_effect)
    _replace_effects(result.biomes, get_biome_effect)
    _replace_effects(result.worlds, get_world_effect)

    return result


def load_assets(data_dir):
    assets_dir = os.path.join(data_dir, "visual")
    colors = yaml.safe_load(open(assets_dir + "/palette.yml", "r", encoding="utf-8"))

    result = Assets(colors=colors)

    return result


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
