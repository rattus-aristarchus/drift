import dataclasses
from dataclasses import field
from typing import List


@dataclasses.dataclass
class Model:

    id: str = ""


@dataclasses.dataclass
class EffectModel(Model):

    effects: List = field(default_factory=lambda: [])


@dataclasses.dataclass
class PopModel(EffectModel):

    name: str = ""
    sapient: bool = False


@dataclasses.dataclass
class GroupModel(EffectModel):

    name: str = ""


@dataclasses.dataclass
class BiomeModel(EffectModel):

    capacity: dict = field(default_factory=lambda: {})


@dataclasses.dataclass
class WorldModel(EffectModel):

    width: int = 0
    height: int = 0
    cells: dict = field(default_factory=lambda: {})


@dataclasses.dataclass
class ModelStorage:
    """
    All the data models in the simulation
    """

    pops: List[PopModel] = field(default_factory=lambda: [])
    groups: List[GroupModel] = field(default_factory=lambda: [])
    biomes: List[BiomeModel] = field(default_factory=lambda: [])
    worlds: List[WorldModel] = field(default_factory=lambda: [])

    def get_pop(self, id):
        return self.get(id, self.pops)

    def get_group(self, id):
        return self.get(id, self.groups)

    def get_biome(self, id):
        return self.get(id, self.biomes)

    def get_world(self, id):
        return self.get(id, self.worlds)

    def get(self, id: str, model_list):
        for entity in model_list:
            if entity.id == id:
                return entity
        return None
