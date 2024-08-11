import dataclasses
from dataclasses import field

from src.logic.entities.basic.entities import Entity


@dataclasses.dataclass
class Agent(Entity):
    """
    Нечто, обладающее "эффектами" - уравнениями, которые
    вычисляются в каждую итерацию системы.
    """

    effects: list = field(default_factory=lambda: [])

    def do_effects(self, cell_buffer=None, grid_buffer=None):
        """
        Вызывается каждую итерацию.
        """
        for func in self.effects:
            func(self, cell_buffer, grid_buffer)


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
