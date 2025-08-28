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

    # Чтение можно производить только из объектов прошлой итерации,
    # а запись - только в текущую (потому что иначе порядок выполнения)
    # агентов будет влиять на результаты вычислений).
    # Чтобы не возникало путаницы на уровне эффектов, в кждый эффект мы
    # передаём отдельно объект для чтения (=объект прошлой итерации) и
    # объект для записи.
    def do_effects(self, agent_read, cell_write, cell_read, buffer):
        """
        Вызывается каждую итерацию.
        """
        for func in self.effects:
            func(self, agent_read, cell_write, cell_read, buffer)
