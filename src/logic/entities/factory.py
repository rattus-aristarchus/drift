from src.logic import util
from kivy import Logger

from src.logic.entities.basic import entities


class Factory:

    def __init__(self):
        self.populations = []
        self.structures = []
        self.resources = []
        self.biomes = []

    def new_population(self, name):
        return self.new(self.populations, name)

    def new_structure(self, name):
        return self.new(self.structures, name)

    def new_resource(self, name):
        return self.new(self.resources, name)

    def new_biome(self, name):
        return self.new(self.biomes, name)

    def new(self, prototype_list, name):
        prototype = _get(name, prototype_list)
        if not prototype:
            _log_bad_name(name, type)
            return None
        else:
            result = entities.deep_copy_simple(prototype)
            return result


def _get(name, prototype_list):
    for entity in prototype_list:
        if entity.name == name:
            return entity
    return None

def _log_bad_name(name, entity_type):
    Logger.error(f"Trying to create {entity_type} of none-existent type {name}.")
