import dataclasses
from dataclasses import field
import yaml

from src.logic.models import custom_fields


@dataclasses.dataclass
class Model(yaml.YAMLObject):

    yaml_loader = yaml.SafeLoader
    id: str = ""


@dataclasses.dataclass
class EffectModel(Model):

    yaml_tag = '!effect'

    effects: list = field(default_factory=lambda: [])


@dataclasses.dataclass
class PopModel(EffectModel):

    yaml_tag = '!population'

    name: str = ""
    sapient: bool = False
    type: str = ""
    yearly_growth: float = 0.0
    # loaded as strings, replaced with resource_model
    produces: list = custom_fields.model_list()
    sells: list = custom_fields.model_list()
    looks_for: list = field(default_factory=lambda: [])
    needs: list = field(default_factory=lambda: [])


@dataclasses.dataclass
class StructureModel(EffectModel):

    yaml_tag = '!structure'

    name: str = ""


@dataclasses.dataclass
class ResourceModel(EffectModel):

    yaml_tag = '!resource'

    type: str = ""
    yearly_growth: float = 0.0
    inputs: list = custom_fields.model_list()
    min_labor: int = 0
    max_labor: int = 0
    max_labor_share: float = 0.0
    productivity: float = 1.0


@dataclasses.dataclass
class NeedModel(Model):

    yaml_tag = '!need'

    resource: ResourceModel = None
    type: str = ""
    per_1000: int = 0


@dataclasses.dataclass
class BiomeModel(EffectModel):

    yaml_tag = '!biome'

    capacity: dict = field(default_factory=lambda: {})
    # список из пар модель ресурса + количество
    resources: list = custom_fields.model_list_list()
    moisture: str = ""


@dataclasses.dataclass
class CellModel(Model):

    yaml_tag = '!cell'

    x: int = 0
    y: int = 0
    biome: BiomeModel = None
    resources: list = field(default_factory=lambda: [])
    pops: list = field(default_factory=lambda: [])
    groups: list = field(default_factory=lambda: [])


@dataclasses.dataclass
class WorldModel(EffectModel):

    yaml_tag = '!world'

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

    yaml_tag = '!grid'

    # a list of columns, each of which is a list of cells;
    cell_matrix: list = field(default_factory=lambda: [])


"""
Настало время черной магии
"""


def prepare_yaml(_model_class):
    for _class in _model_class.__subclasses__():
        _register_constructor(_class)
        prepare_yaml(_class)


def _register_constructor(dataclass_type):
    yaml.SafeLoader.add_constructor(
        tag=dataclass_type.yaml_tag,
        constructor=lambda loader, node: _custom_constructor(loader, node, dataclass_type)
    )


def _custom_constructor(loader, node, dataclass_type):
    data = loader.construct_mapping(node, deep=True)
    return dataclass_type(**data)


"""
Конец черной магии. Отправляемся в церковь или кабак, запивать или замаливать совесть. 
"""

# возможно, стоит засунуть этот вызов в какое-то более явное место
prepare_yaml(Model)
