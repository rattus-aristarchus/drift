import dataclasses
from dataclasses import field
from typing import List

from src.logic import util
from src.logic.entities import entities
from src.logic.entities.agents import Agent, Resource
from src.logic.entities.entities import Entity
from src.logic.models import StructureModel, ResourceModel


@dataclasses.dataclass
class Structure(Agent):
    """
    Социальные структуры, состоящие из нескольких
    популяций / территорий (города, государства, рынки).
    """

    effects: list = field(default_factory=lambda: [])
    pops: list = field(default_factory=lambda: [])
    # a list of cells
    territory: list = field(default_factory=lambda: [])
    resources: list = field(default_factory=lambda: [])

    def do_effects(self, cell_buffer=None, grid_buffer=None):
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
class Commodity:

    seller: Agent = None
    amount: int = 0


@dataclasses.dataclass
class Market(Agent):

    # рынок создается для каждого отдельного вида продукта
    product: Resource = None
    type: str = ""
    exchange: Resource = None
    sale: Commodity = None
    purchases: list[Commodity] = field(default_factory=lambda: [])
    price: float = 0.0


def create_market(model, cell, type, resource=None):
    market = Market(
        type=type
    )
    if resource:
        market.product = resource
    market.effects = model.effects
    cell.markets.append(market)
    return market


def create_structure(model: StructureModel, destination=None, grid=None):
    result = Structure(name=model.id)
    result.effects = list(model.effects)
    if destination:
        destination.structures.append(result)
        result.territory.append(destination)
    if grid:
        grid.structures.append(result)
    return result


def copy_structure(structure, destination=None, grid=None):
    result = entities.copy_entity(structure)

    if destination:
        destination.structures.append(result)
        result.territory.append(destination)

    if grid:
        grid.structures.append(result)

        # what was copied was entities from the former
        # iteration of the grid. now, we have to find
        # their equivalents in the next iteration
        territories = []
        for territory in result.territory:
            territories.append(territory.next_copy)
        result.territory = territories

        pops = []
        for pop in result.pops:
            pops.append(pop.next_copy)
            pop.next_copy.structures.append(result)
        result.pops = pops

        resources = []
        for res in result.resources:
            resources.append(res.next_copy)
        result.resources = resources

    return result

