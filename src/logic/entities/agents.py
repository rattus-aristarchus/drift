import dataclasses
from dataclasses import field
from typing import List


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
    # for some unfathomable reason get_pop_effect here is none

    new_pop = Population(name=model.id)
    new_pop.effects = list(model.effects)
    new_pop.sapient = model.sapient
    new_pop.type = model.type

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
    new_pop.effects = list(pop.effects)
    destination.pops.append(new_pop)
    return new_pop


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


@dataclasses.dataclass
class Population(Agent):

    group: Group = None
    size: int = 0
    age: int = 0
    sapient: bool = False
    type: str = ""
