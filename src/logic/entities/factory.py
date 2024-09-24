from kivy import Logger

from src.logic.entities.basic import entities


class Factory:

    def __init__(self):
        self.populations = {}
        self.structures = {}
        self.resources = {}
        self.biomes = {}
        self.misc = {}

    def new_population(self, name):
        new_pop = self._new(self.populations, name)
        # чтобы в первый ход существовния популяции, когда еще
        # не успели рассчитать реальные потребности, не было эффекта кризиса
        for need in new_pop.needs:
            need.actual = need.per_1000
        return new_pop

    def new_structure(self, name):
        return self._new(self.structures, name)

    def new_resource(self, name):
        return self._new(self.resources, name)

    def new_biome(self, name):
        return self._new(self.biomes, name)

    def new_misc(self, name):
        return self._new(self.misc, name)

    def _new(self, prototype_dict, name):
        if name not in prototype_dict.keys():
            Logger.error(f"Trying to create entity of none-existent type {name}.")
            return None
        else:
            prototype = prototype_dict[name]
            return entities.inherit_prototype_fields(prototype)

    def prototype_population(self, name):
        return self._get_prototype(self.populations, name)

    def prototype_structure(self, name):
        return self._get_prototype(self.structures, name)

    def prototype_resource(self, name):
        return self._get_prototype(self.resources, name)

    def prototype_biome(self, name):
        return self._get_prototype(self.biomes, name)

    def prototype_misc(self, name):
        return self._get_prototype(self.misc, name)

    def _get_prototype(self, prototype_dict, name):
        if name not in prototype_dict.keys():
            Logger.error(f"Trying to get an entity with name {name} that is not in a dictionary of all entities.")
            return None
        else:
            return prototype_dict[name]
