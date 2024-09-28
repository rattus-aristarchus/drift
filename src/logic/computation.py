import dataclasses
from dataclasses import field

from src.logic.entities.basic.entities import Entity


class CellCPU:
    pass


class GridCPU:
    pass


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
