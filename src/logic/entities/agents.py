import dataclasses
from dataclasses import field
from typing import List
from src.logic.entities import entities
from src.logic.entities.entities import Entity
from src.logic.models import ResourceModel, PopModel


def create_pop(model: PopModel, destination=None):
    new_pop = Population(
        name=model.id,
        effects=list(model.effects),
        sapient=model.sapient,
        type=model.type,
        sustained_by=model.sustained_by,
        yearly_growth=model.yearly_growth
    )
    new_pop.model = model

    if destination:
        destination.pops.append(new_pop)

    return new_pop


def copy_pop(pop, destination):
    """
    The copy of the pop refers to the same structures
    as the old one.
    """

    new_pop = entities.copy_entity(pop)
    destination.pops.append(new_pop)
    return new_pop


def copy_res(res, destination, new_owner=None):
    copy = entities.copy_entity(res)
    destination.resources.append(copy)
    if new_owner:
        copy.owners = new_owner

    return copy


def create_resource(model: ResourceModel, destination=None, group=None):
    result = Resource(
        name=model.id,
        effects=model.effects,
        yearly_growth=model.yearly_growth,
        type=model.type
    )
    result.model = model
    if destination:
        destination.resources.append(result)
    elif group:
        group.resources.append(result)
    return result


@dataclasses.dataclass
class Agent(Entity):
    """
    Нечто, обладающее "эффектами" - уравнениями, которые
    вычисляются в каждую итерацию системы.
    """

    effects: List = field(default_factory=lambda: [])

    def do_effects(self, cell_buffer=None, grid_buffer=None):
        """
        Вызывается каждую итерацию.
        """
        for func in self.effects:
            func(self, cell_buffer, grid_buffer)


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
    # from 0 to 1:
    hunger: float = 0
    sustained_by: dict = field(default_factory=lambda: {})
    structures: list = field(default_factory=lambda: [])


@dataclasses.dataclass
class Resource(Agent):
    """
    Ресурс. То, что используют популяции; то, что может быть собственностью;
    то, чего может нехватать.
    """

    size: int = 0
    # пары из агент + количество (кто сколько владеет)
    owners: dict = field(default_factory=lambda: {})
    yearly_growth: float = 0.0
    type: str = ""

    def set_owner(self, agent, amount):
        if amount <= 0:
            self.owners.pop(agent.name, None)
        else:
            self.owners[agent.name] = amount

    def get_free_amount(self):
        free = self.size
        for name, amount in self.owners.items():
            free -= amount
        if free < 0:
            free = 0
        return free

