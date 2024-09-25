import dataclasses
import inspect
from dataclasses import field
import yaml

from src.logic.entities.agents.agents import Agent
from src.logic.entities.agents.populations import Population, Need
from src.logic.entities.agents.resources import Resource
from src.logic.entities.agents.structures import Structure, Market
from src.logic.entities.cells import Biome, Cell
from src.logic.entities.histories import World

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
class AgentModel(Model):

    yaml_tag = '!agent'
    linked_class = Agent

@dataclasses.dataclass
class PopModel(AgentModel):

    yaml_tag = '!population'
    linked_class = Population


@dataclasses.dataclass
class StructureModel(AgentModel):

    yaml_tag = '!structure'
    linked_class = Structure


@dataclasses.dataclass
class MarketModel(AgentModel):

    yaml_tag = '!market'
    linked_class = Market


@dataclasses.dataclass
class ResourceModel(AgentModel):

    yaml_tag = '!resource'
    linked_class = Resource


@dataclasses.dataclass
class NeedModel(AgentModel):

    yaml_tag = '!need'
    linked_class = Need


@dataclasses.dataclass
class BiomeModel(AgentModel):

    yaml_tag = '!biome'
    linked_class = Biome


@dataclasses.dataclass
class CellModel(AgentModel):

    yaml_tag = '!cell'

    groups: list = field(default_factory=lambda: [])


@dataclasses.dataclass
class WorldModel(AgentModel):

    yaml_tag = '!world'
    linked_class = World

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

    instance = dataclass_type()

    # при выставлении полей через setattr нам
    # не надо прописывать их отдельно в классах моделей
    for k, v in data.items():
        setattr(instance, k, v)

    return instance

# возможно, стоит засунуть этот вызов в какое-то более явное место
_register_constructors_for_model_subclasses(Model)

"""
Конец черной магии. Отправляемся в церковь или кабак, запивать или замаливать совесть. 
"""

"""
def _create_fields_for_model_recursive(model_cls):
    _create_fields_for_model(model_cls)

    for _class in model_cls.__subclasses__():
        _create_fields_for_model_recursive(model_cls)

def _create_fields_for_model(model_cls):
    linked_cls = model_cls.linked_class
    for field in dataclasses.fields(linked_cls):
        setattr()
        field.default
        value = getattr(to_copy, field.name)
        if isinstance(value, list) or isinstance(value, dict):
            setattr(copy, field.name, value.copy())


_create_fields_for_model_recursive(Model)
"""

def create_from_model(model):
    new_entity = model.linked_class()
    return _fill_from_model(model, new_entity)

def _fill_from_model(model, entity):
    for field_name, value in _get_model_fields(model):

        # if some of the model's fields are models too,
        # they have to be replaced with actual objects as well
        new_value = _replace_models(value)

        setattr(entity, field_name, new_value)
    return entity

def _get_model_fields(model):
    result = []
    for i in inspect.getmembers(model):

        # to remove private and protected
        # functions
        if not i[0].startswith('_'):

            # To remove other methods that
            # dont start with a underscore
            if not inspect.ismethod(i[1]):
                result.append(i)

    return result


def _replace_models(value):
    """
    Replace models recursively with objects derived from those models
    """

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
