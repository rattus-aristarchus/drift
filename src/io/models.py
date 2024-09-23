import dataclasses
import uuid
from dataclasses import field
import yaml

from src.logic.entities.agents.populations import Population, Need
from src.logic.entities.agents.resources import Resource
from src.logic.entities.agents.structures import Structure, Market
from src.logic.entities.cells import Biome, Cell
from src.logic.entities.histories import World
from src.logic.rules.rules import BiomeRule, ResourceRule, PopulationRule

"""
При переносе данных из моделей в связанные с ними классы система
ищет одинаковые поля у модели, и у класса. Чтобы не прописывать 
эти поля у модели в ручную, она тупо наследует от связанного класса. 
"""


@dataclasses.dataclass
class Model(yaml.YAMLObject):

    yaml_loader = yaml.SafeLoader
    linked_class = None

    name: str = ""


@dataclasses.dataclass
class PopModel(Model, Population):

    yaml_tag = '!population'
    linked_class = Population


@dataclasses.dataclass
class StructureModel(Model, Structure):

    yaml_tag = '!structure'
    linked_class = Structure


@dataclasses.dataclass
class MarketModel(Model, Market):

    yaml_tag = '!market'
    linked_class = Market


@dataclasses.dataclass
class ResourceModel(Model, Resource):

    yaml_tag = '!resource'
    linked_class = Resource


@dataclasses.dataclass
class NeedModel(Model, Need):

    yaml_tag = '!need'
    linked_class = Need


@dataclasses.dataclass
class BiomeModel(Model, Biome):

    yaml_tag = '!biome'
    linked_class = Biome


@dataclasses.dataclass
class CellModel(Model, Cell):

    yaml_tag = '!cell'

    groups: list = field(default_factory=lambda: [])


@dataclasses.dataclass
class WorldModel(Model, World):

    yaml_tag = '!world'
    linked_class = World

"""
Дальше - модели для правил
"""

@dataclasses.dataclass
class BiomeRuleModel(Model, BiomeRule):

    yaml_tag = '!biome_rule'
    linked_class = BiomeRule


@dataclasses.dataclass
class ResourceRuleModel(Model, BiomeRule):

    yaml_tag = '!resource_rule'
    linked_class = ResourceRule


@dataclasses.dataclass
class PopulationRuleModel(Model, BiomeRule):
    yaml_tag = '!population_rule'
    linked_class = PopulationRule


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

# возможно, стоит засунуть этот вызов в какое-то более явное место
_register_constructors_for_model_subclasses(Model)

for _class in _model_class.__subclasses__():
    _register_constructor(_class)
    _register_constructors_for_model_subclasses(_class)
"""
Конец черной магии. Отправляемся в церковь или кабак, запивать или замаливать совесть. 
"""

def _create_fields_for_model_recursive(model_cls):



_create_fields_for_model_recursive(Model)


def create_from_model(model):
    new_entity = model.linked_class()
    return _fill_from_model(model, new_entity)

def _fill_from_model(model, entity):
    for model_field in dataclasses.fields(type(model)):
        if model_field.name == "id":
            continue
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
