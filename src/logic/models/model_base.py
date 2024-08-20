import dataclasses
from dataclasses import field

from src.logic.models.models import PopModel, StructureModel, ResourceModel, BiomeModel, WorldModel, GridModel


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
    maps: list[GridModel] = field(default_factory=lambda: [])

    def get_pop(self, id):
        return self.get(id, self.pops)

    def get_structure(self, id):
        return self.get(id, self.structures)

    def get_res(self, id):
        return self.get(id, self.resources)

    def get_biome(self, id):
        return self.get(id, self.biomes)

    def get_world(self, id):
        return self.get(id, self.worlds)

    def get_map(self, id):
        return self.get(id, self.maps)

    def get(self, id: str, model_list):
        for entity in model_list:
            if entity.id == id:
                return entity
        return None
