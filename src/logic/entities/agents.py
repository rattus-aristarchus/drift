import dataclasses
import os
from dataclasses import field
from typing import List
from src.logic.entities import entities
from src.logic.entities.entities import Entity
from src.logic.models import ResourceModel, PopModel, NeedModel


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

    structures: list = field(default_factory=lambda: [])
    owned_resources: list = field(default_factory=lambda: [])
    # what fraction of labor is spent on what
    effort: dict = field(default_factory=lambda: {})
    # how much surplus did each production net
    surplus: dict = field(default_factory=lambda: {})

    needs: list = field(default_factory=lambda: [])

    def __str__(self):
        if self.type == "":
            title = f"{self.name}"
        else:
            title = f"{self.name} ({self.type})"
        description = (
            f"{title}: {self.size}{os.linesep}"
            f"возраст: {self.age}; голод: {self.hunger}")
        return description

    def get_need(self, need_type="", need_id=""):
        if need_type != "":
            for need in self.needs:
                if need.model.type == need_type:
                    return need

        elif need_id != "":
            for need in self.needs:
                if need.model.id == need_id:
                    return need

        return None


@dataclasses.dataclass
class Need(Entity):
    """
    Потребность популяции в определенных ресурсах.
    """

    # сколько нужно на 1000 популяции
    per_1000: int = 0
    # сколько реально есть
    actual: int = 0


@dataclasses.dataclass
class Resource(Agent):
    """
    Ресурс. То, что используют популяции; то, что может быть собственностью;
    то, чего может нехватать.
    """

    size: int = 0
    # пары из имя агента + количество (кто сколько владеет)
    owners: dict = field(default_factory=lambda: {})
    yearly_growth: float = 0.0
    type: str = ""

    def __str__(self):
        if self.type == "":
            title = f"{self.name}"
        else:
            title = f"{self.name} ({self.type})"
        description = (
            f"{title}: {self.size}"
        )
        if len(self.owners) > 0:
            description += f"{os.linesep}владельцы:"
            for owner, amount in self.owners.items():
                description += f"{os.linesep}{owner}: {amount}"
        return description

    def get_free_amount(self):
        free = self.size
        for name, amount in self.owners.items():
            if amount > 0:
                free -= amount
        if free < 0:
            free = 0
        return free


def create_pop(model: PopModel, destination=None):
    new_pop = Population(
        name=model.id,
        effects=list(model.effects),
        sapient=model.sapient,
        type=model.type,
        yearly_growth=model.yearly_growth
    )
    new_pop.model = model

    needs = []
    for need_model in model.needs:
        needs.append(create_need(need_model))
    new_pop.needs = needs

    if destination:
        destination.pops.append(new_pop)

    return new_pop


def create_need(model: NeedModel):
    result = Need(
        per_1000=model.per_1000
    )
    result.model = model
    return result


def copy_pop_without_owned(pop, destination):
    """
    The copy of the pop refers to the same structures
    as the old one.
    """

    new_pop = entities.copy_entity(pop)
    destination.pops.append(new_pop)
    return new_pop


def copy_res_without_owners(res, destination):
    copy = entities.copy_entity(res)
    destination.resources.append(copy)
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


def set_ownership(agent, resource, amount=None):
    """
    Сделать agent владельцем amount ресурса resource.

    Сумма количеств по всем ресурсам никак не контролируется,
    она может оказаться больше общего количества ресурса (при
    ошибке в подсчетах).
    """

    if amount is None:
        resource.owners[agent.name] = resource.size
        if resource not in agent.owned_resources:
            agent.owned_resources.append(resource)

    elif amount <= 0:
        resource.owners.pop(agent.name, None)
        if resource in agent.owned_resources:
            agent.owned_resources.remove(resource)

    else:
        resource.owners[agent.name] = amount
        if resource not in agent.owned_resources:
            agent.owned_resources.append(resource)


def add_ownership(agent, resource, amount):
    if agent.name not in resource.owners.keys():
        resource.owners[agent.name] = 0
    resource.owners[agent.name] += amount

    if resource not in agent.owned_resources:
        agent.owned_resources.append(resource)


def subtract_ownership(agent, resource, amount):
    current = resource.owners[agent.name]

    if current <= amount:
        resource.owners.pop(agent.name, None)
        agent.owned_resources.remove(resource)
    else:
        resource.owners[agent.name] -= amount


def remove_ownership(population, resource):
    set_ownership(population, resource, 0)

#    resource.set_owner(population, 0)
#    if resource in population.owned_resources:
#        population.owned_resources.remove(resource)
