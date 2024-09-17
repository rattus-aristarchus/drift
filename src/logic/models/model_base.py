import dataclasses
from dataclasses import field

from src.logic.models.models import PopModel, StructureModel, ResourceModel, BiomeModel, WorldModel


@dataclasses.dataclass
class ModelBase:
    """
    All the data models in the simulation
    """

    pops: list[PopModel] = field(default_factory=lambda: [])
    structures: list[StructureModel] = field(default_factory=lambda: [])
    resources: list[ResourceModel] = field(default_factory=lambda: [])
    biomes: list[BiomeModel] = field(default_factory=lambda: [])
    worlds: list[WorldModel] = field(default_factory=lambda: [])


    def get_pop(self, name):
        return self.get(name, self.pops)

    def get_structure(self, name):
        return self.get(name, self.structures)

    def get_res(self, name):
        return self.get(name, self.resources)

    def get_biome(self, name):
        return self.get(name, self.biomes)

    def get_world(self, name):
        return self.get(name, self.worlds)

    def get(self, name: str, model_list):
        for entity in model_list:
            if entity.name == name:
                return entity
        return None
