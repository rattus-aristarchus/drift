import dataclasses
import os

from src.logic.entities.basic.entities import Entity


@dataclasses.dataclass
class Biome(Entity):
    """
    Экология клетки карты.
    """

    # сколько популяций или ресурсов может вместить данная клетка:
    capacity: dict = dataclasses.field(default_factory=lambda: {})
    starting_resources: list = dataclasses.field(default_factory=lambda: [])
    moisture: str = ""

    def __str__(self):
        description = self.name
        if len(self.capacity) > 0:
            description += f"{os.linesep}вместимость:"
            for pop_type, amount in self.capacity.items():
                description += f"{os.linesep}{pop_type}: {amount}"
        return description

    def get_capacity(self, pop_name):
        if pop_name in self.capacity.keys():
            return self.capacity[pop_name]
        else:
            return 0
