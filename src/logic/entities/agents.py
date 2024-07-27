import dataclasses
from dataclasses import field
from typing import List, Dict
from src.logic.models import ResourceModel
from src.logic import util


def create_structure(model, destination):
    new_structure = Structure(name=model.id)
    new_structure.effects = list(model.effects)
    destination.structures.append(new_structure)
    new_structure.territory.append(destination)
    return new_structure


def copy_structure(structure, destination):
    result = copy_entity(structure)
    destination.structures.append(result)
    result.territory.append(destination)
    return result


def create_pop(model, destination=None):
    new_pop = Population(name=model.id)
    new_pop.effects = list(model.effects)
    new_pop.sapient = model.sapient
    new_pop.type = model.type
    new_pop.sustained_by = model.sustained_by
    new_pop.yearly_growth = model.yearly_growth

    if destination:
        destination.pops.append(new_pop)

    return new_pop


def copy_pop(pop, destination):
    """
    The copy of the pop refers to the same structures
    as the old one.
    """

    new_pop = copy_entity(pop)
    destination.pops.append(new_pop)
    return new_pop


def copy_res(res, destination, new_owner=None):
    copy = copy_entity(res)
    destination.resources.append(copy)
    if new_owner:
        copy.owner = new_owner

    return copy


def create_resource(model: ResourceModel, destination=None, group=None):
    result = Resource(
        name=model.id,
        effects=model.effects,
        yearly_growth=model.yearly_growth,
        type=model.type
    )
    if destination:
        destination.resources.append(result)
    elif group:
        group.resources.append(result)
    return result


def copy_entity(entity):
    copy = util.copy_dataclass_with_collections(entity)
    copy.last_copy = entity
    return copy


@dataclasses.dataclass
class Entity:
    """
    База
    """

    name: str = ""
    # при создании новой итерации модели все сущности
    # копируются в нее; last_copy - ссылка на сущность
    # в прошлой итерации
    last_copy = None


@dataclasses.dataclass
class Agent(Entity):
    """
    Нечто, обладающее "эффектами" - уравнениями, которые
    вычисляются в каждую итерацию системы.
    """

    effects: List = field(default_factory=lambda: [])

    def do_effects(self, cell_buffer, grid_buffer):
        """
        Вызывается каждую итерацию.
        """
        for func in self.effects:
            func(self, cell_buffer, grid_buffer)


@dataclasses.dataclass
class Structure(Entity):
    """
    Социальные структуры, состоящие из нескольких
    популяций / территорий (города, государства, рынки).
    """

    effects: List = field(default_factory=lambda: [])
    pops: List = field(default_factory=lambda: [])
    # a list of cells
    territory: List = field(default_factory=lambda: [])
    resources: List = field(default_factory=lambda: [])

    def do_effects(self, grid_buffer):
        for func in self.effects:
            func(self, grid_buffer)

    def get_res(self, name):
        for res in self.resources:
            if res.name == name:
                return res
        return None

    def get_pop(self, name):
        for pop in self.pops:
            if pop.name == name:
                return pop
        return None


@dataclasses.dataclass
class Population(Agent):
    """
    Популяция. Ну блин, когда у нас исчислимое нечто, и оно что-то делает.
    """

    size: int = 0
    age: int = 0
    sapient: bool = False
    type: str = ""
    yearly_growth: float = 0.0
    sustained_by: dict = field(default_factory=lambda: {})
    structures: list[Structure] = field(default_factory=lambda: [])


@dataclasses.dataclass
class Resource(Agent):
    """
    Ресурс. То, что используют популяции; то, что может быть собственностью;
    то, чего может нехватать.
    """

    size: int = 0
    owner: Agent = None
    yearly_growth: float = 0.0
    type: str = ""
