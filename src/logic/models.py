import dataclasses
from dataclasses import field
from typing import List, Dict


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
    type: str = ""
    yearly_growth: float = 0.0
    # loaded as strings, replaced with resource_model
    produces: list = field(default_factory=lambda: [])
    looks_for: list = field(default_factory=lambda: [])
    needs: list = field(default_factory=lambda: [])


@dataclasses.dataclass
class StructureModel(EffectModel):

    name: str = ""


@dataclasses.dataclass
class ResourceModel(EffectModel):

    type: str = ""
    yearly_growth: float = 0.0
    inputs: list = field(default_factory=lambda: [])
    min_labor: int = 0
    max_labor: int = 0
    max_labor_share: float = 0.0


@dataclasses.dataclass
class NeedModel(Model):
    resource: ResourceModel = None
    type: str = ""
    per_1000: int = 0


@dataclasses.dataclass
class BiomeModel(EffectModel):

    capacity: dict = field(default_factory=lambda: {})
    # список из пар модель ресурса + количество
    resources: list = field(default_factory=lambda: [])
    moisture: str = ""


@dataclasses.dataclass
class CellModel(Model):

    x: int = 0
    y: int = 0
    biome: BiomeModel = None
    resources: List = field(default_factory=lambda: [])
    pops: List = field(default_factory=lambda: [])
    groups: List = field(default_factory=lambda: [])


@dataclasses.dataclass
class WorldModel(EffectModel):

    width: int = 10
    height: int = 10
    age: int = 0
    mean_temp: float = 7
    # how much the temperature needs to deviate for
    # pops to change by 50%:
    deviation_50: float = 1

    map: str = ""
    # инструкции для наполнения регионов
    cell_instructions: dict = field(default_factory=lambda: {})


@dataclasses.dataclass
class GridModel(Model):

    # a list of columns, each of which is a list of cells;
    cell_matrix: List = field(default_factory=lambda: [])


@dataclasses.dataclass
class ModelStorage:
    """
    All the data models in the simulation
    """

    pops: List[PopModel] = field(default_factory=lambda: [])
    structures: List[StructureModel] = field(default_factory=lambda: [])
    resources: List[ResourceModel] = field(default_factory=lambda: [])
    biomes: List[BiomeModel] = field(default_factory=lambda: [])
    worlds: List[WorldModel] = field(default_factory=lambda: [])
    maps: List[GridModel] = field(default_factory=lambda: [])

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
