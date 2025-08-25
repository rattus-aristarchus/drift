from src.logic.entities.basic import entities
from src.logger import CustomLogger

logger = CustomLogger(__name__)

class Factory:

    def __init__(self):
        self.populations = {}
        self.structures = {}
        self.resources = {}
        self.biomes = {}
        self.misc = {}

        self.worlds = {}

    def new_population(self, name, fields=None):
        new_pop = self._new(self.populations, name, fields)
        # чтобы в первый ход существовния популяции, когда еще
        # не успели рассчитать реальные потребности, не было эффекта кризиса
        for need in new_pop.needs:
            need.actual = need.per_1000
        return new_pop

    def new_structure(self, name, fields=None):
        return self._new(self.structures, name, fields)

    def new_resource(self, name, cell=None, fields=None):
        new = self._new(self.resources, name, fields)
        if cell:
            cell.resources.append(new)
        return new

    def new_biome(self, name, fields=None):
        return self._new(self.biomes, name, fields)

    def new_misc(self, name, fields=None):
        return self._new(self.misc, name, fields)

    def prototype_population(self, name):
        return self._get_from_dict(self.populations, name)

    def prototype_structure(self, name):
        return self._get_from_dict(self.structures, name)

    def prototype_resource(self, name):
        return self._get_from_dict(self.resources, name)

    def prototype_biome(self, name):
        return self._get_from_dict(self.biomes, name)

    def prototype_misc(self, name):
        return self._get_from_dict(self.misc, name)

    def get_world(self, name):
        return self._get_from_dict(self.worlds, name)

    def _get_from_dict(self, _dict, name):
        if name not in _dict.keys():
            logger.error(f"Trying to get an entity with name {name} that is not in a dictionary of all entities.")
            return None
        else:
            return _dict[name]

    def _new(self, prototype_dict, name, fields=None):
        if name not in prototype_dict.keys():
            logger.error(f"Trying to create entity of none-existent type {name}.")
            return None
        elif fields is not None:
            prototype = prototype_dict[name]
            result = entities.inherit_prototype_fields(prototype)
            entities.override_fields(result, fields)
            return result
        else:
            prototype = prototype_dict[name]
            return entities.inherit_prototype_fields(prototype)


def get_factory_with_world_name(name, factories):
    for factory in factories:
        for world_name, world in factory.worlds.items():
            if world_name == name:
                return factory
    return None
