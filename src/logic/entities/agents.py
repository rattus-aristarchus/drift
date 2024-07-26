import dataclasses
from dataclasses import field
from typing import List, Dict

from src.logic.models import ResourceModel


def create_group(model, destination):
    new_group = Group(name=model.id)
    new_group.effects = list(model.effects)
    destination.groups.append(new_group)
    new_group.territory.append(destination)
    return new_group


def copy_group(group, destination):
    new_group = Group(name=group.name)
    new_group.effects = list(group.effects)
    destination.groups.append(new_group)
    new_group.territory.append(destination)
    return new_group


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
    new_pop = Population(name=pop.name)
    new_pop.size = pop.size
    new_pop.age = pop.age
    new_pop.group = pop.group
    new_pop.sapient = pop.sapient
    new_pop.type = pop.type
    new_pop.yearly_growth = pop.yearly_growth
    new_pop.effects = list(pop.effects)
    new_pop.sustained_by = dict(pop.sustained_by)
    destination.pops.append(new_pop)
    return new_pop


def copy_res(res, destination, new_owner=None):
    copy = dataclasses.replace(res)
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


@dataclasses.dataclass
class Entity:

    name: str = ""


@dataclasses.dataclass
class Agent:

    name: str
    effects: List = field(default_factory=lambda: [])

    def do_effects(self, cell_buffer, grid_buffer):
        for func in self.effects:
            func(self, cell_buffer, grid_buffer)


@dataclasses.dataclass
class Group(Agent):

    pops: List = field(default_factory=lambda: [])
    # a list of cells
    territory: List = field(default_factory=lambda: [])
    resources: List = field(default_factory=lambda: [])

    def do_effects(self, cell_buffer, grid_buffer):
        for resource in self.resources:
            resource.do_effects()
        for func in self.effects:
            func(self, cell_buffer, grid_buffer)

    # TODO: fetcher methods for resources


@dataclasses.dataclass
class Population(Agent):

    group: Group = None
    size: int = 0
    age: int = 0
    sapient: bool = False
    type: str = ""
    yearly_growth: float = 0.0
    sustained_by: Dict = field(default_factory=lambda: {})


@dataclasses.dataclass
class Resource(Agent):

    size: int = 0
    owner: Agent = None
    yearly_growth: float = 0.0
    type: str = ""
