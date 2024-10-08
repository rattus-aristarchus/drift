import dataclasses
import os
from dataclasses import field

from src.logic.entities.agents.agents import Agent
from src.logic.entities.basic.recurrents import Recurrent


@dataclasses.dataclass
class Resource(Agent, Recurrent):
    """
    Ресурс. То, что используют популяции; то, что может быть собственностью;
    то, чего может нехватать.
    """

    size: int = 0
    # пары из имя агента + количество (кто сколько владеет)
    owners: dict = field(default_factory=lambda: {})
    yearly_growth: float = 0.0

    type: str = ""
    inputs: list = field(default_factory=lambda: [])
    min_labor: int = 0
    max_labor: int = 0
    max_labor_share: float = 0.0
    productivity: float = 1.0
    movable: bool = True

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
