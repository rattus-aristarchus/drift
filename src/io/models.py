import dataclasses
from dataclasses import field
import yaml

from src.logic.entities.agents.populations import Population, Need
from src.logic.entities.agents.resources import Resource
from src.logic.entities.agents.structures import Structure
from src.logic.entities.cells import Biome
from src.logic.entities.histories import World


@dataclasses.dataclass
class Model(yaml.YAMLObject):

    yaml_loader = yaml.SafeLoader
    name: str = ""


@dataclasses.dataclass
class EffectModel(Model):

    yaml_tag = '!effect'

    effects: list = field(default_factory=lambda: [])


@dataclasses.dataclass
class PopModel(EffectModel):

    yaml_tag = '!population'
    linked_class = Population

    sapient: bool = False
    type: str = ""
    yearly_growth: float = 0.0
    produces: list = field(default_factory=lambda: [])
    sells: list = field(default_factory=lambda: [])
    looks_for: list = field(default_factory=lambda: [])
    needs: list = field(default_factory=lambda: [])


@dataclasses.dataclass
class StructureModel(EffectModel):

    yaml_tag = '!structure'
    linked_class = Structure


@dataclasses.dataclass
class ResourceModel(EffectModel):

    yaml_tag = '!resource'
    linked_class = Resource

    type: str = ""
    yearly_growth: float = 0.0
    inputs: list = field(default_factory=lambda: [])
    min_labor: int = 0
    max_labor: int = 0
    max_labor_share: float = 0.0
    productivity: float = 1.0


@dataclasses.dataclass
class NeedModel(Model):

    yaml_tag = '!need'
    linked_class = Need

    resource: str = ""
    type: str = ""
    per_1000: int = 0


@dataclasses.dataclass
class BiomeModel(EffectModel):

    yaml_tag = '!biome'
    linked_class = Biome

    capacity: dict = field(default_factory=lambda: {})
    # список из пар модель ресурса + количество
    starting_resources: list = field(default_factory=lambda: [])
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
    linked_class = World

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


"""
Настало время черной магии.

К сожалению, PyYAML не умеет нормально работать с dataclass.field. При инициализации
объекта из файла, обычные поля создаются, а поля dataclass.field - нет. Скорее всего,
это происходит из-за того, что PyYAML не использует автоматически создаваемый dataclass 
конструктор.
Поэтому наша задача - напрямую передать эти конструкторы в PyYAML.
"""


def _register_constructors_for_model_subclasses(_model_class):
    """
    Обходим рекурсивно дерево классов моделей, и для каждого класса
    регистрируем конструктор в PyYAML
    """
    for _class in _model_class.__subclasses__():
        _register_constructor(_class)
        _register_constructors_for_model_subclasses(_class)


def _register_constructor(dataclass_type):
    """
    Передаём в YAML конструктор для этого типа
    """
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
_register_constructors_for_model_subclasses(Model)


def create_from_model(model):
    new_entity = model.linked_class()
    return _fill_from_model(model, new_entity)


def _fill_from_model(model, entity):
    for model_field in dataclasses.fields(type(model)):
        model_value = getattr(model, model_field.name)
        new_value = _replace_models(model_value)
        setattr(entity, model_field.name, new_value)
    return entity

def _replace_models(value):
    result = _replace_if_model(value)
    if isinstance(value, list):
        result = []
        for obj in value:
            new_value = _replace_if_model(obj)
            result.append(new_value)
    elif isinstance(value, dict):
        result = {}
        for key, obj in value.items():
            new_value = _replace_if_model(obj)
            result[key] = new_value
    return result

def _replace_if_model(value):
    result = value
    if isinstance(value, Model):
        result = create_from_model(value)
    return result
