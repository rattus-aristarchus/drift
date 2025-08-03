import dataclasses
from dataclasses import field

from kivy import Logger
from src.logic.entities.basic.entities import Entity


class Buffer:

    def __init__(self, world):
        self.world = world
        self.memory = {}



class GridCPU:
    """
    Главный класс, заведующий выполнением алгоритмов модели
    """


    def __init__(self, world):
        self.grid = None
        self.cpus = []

        self.world = world
        self.effects = world.effects
        self.cell_effects = world.cell_effects

    def refresh_cpus(self, grid):
        """
        Перед выполнением алгоритмов в новой итерации, необходимо получить
        новую карту и создать для каждой клетки управляющий объект.
        """
        self.cpus = []
        self.grid = grid
        for cell in grid.cells_as_list():
            self.cpus.append(
                CellCPU(cell)
            )

    def do_effects(self):
        """
        Выполняем алгоритмы
        """

        # the buffer helps avoid doing some
        # calculations multiple times
        buffer = Buffer(self.world)

        # вначале общие, уровня карты
        for func in self.effects:
            func(self.grid, self.grid.last_copy, buffer)

        self._grid_level_messages(buffer)

        # затем алгоритмы структур
        for structure in self.grid.structures:
            structure.do_effects(None, None, None, buffer)

        # передаем выполнение управляющим объектам для отдельных клеток
        for cell_cpu in self.cpus:
            cell_cpu.do_effects(buffer, self.cell_effects)

    def _grid_level_messages(self, buffer):
        msg = (f"The age is {self.grid.state.age}. Global temeprature"
                f" is {self.grid.state.temperature}.")
        if "temp_deviation" in buffer.memory.keys():
            msg += (f"It deviates from"
                    f" mean by {buffer.memory["temp_deviation"]}.")
        Logger.info(msg)



class CellCPU:
    """
    Класс, заведующий выполнением алгоритмов для отдельной клетки карты.
    """

    def __init__(self, cell):
        self.cell = cell

    def do_effects(self, buffer, cell_effects):
        """
        Выполняем алгоритмы
        """

        # вначале - алгоритмы уровня клетки
        for func in cell_effects:
            func(self.cell, self.cell.last_copy, buffer)

        # алгоритмы для популяций
        for pop in self.cell.pops:
            # если ссылка на last_copy отсутстввует, эта популяция
            # была создана в эту итерацию, и вычислять ее эффекты
            # не нужно
            if pop.last_copy:
                pop.do_effects(pop.last_copy, self.cell, self.cell.last_copy, buffer)

        # алгоритмы для ресурсов
        for resource in self.cell.resources:
            if resource.last_copy:
                resource.do_effects(resource.last_copy, self.cell, self.cell.last_copy, buffer)

        # алгоритмы для рынков
        for market in self.cell.markets:
            market.do_effects(None, self.cell, self.cell.last_copy, buffer)

        # удаляем вымершие популяции
        # remove pops that have died out
        to_remove = []
        for pop in self.cell.pops:
            if pop.size <= 0:
                to_remove.append(pop)
        for pop in to_remove:
            self.cell.pops.remove(pop)

        # убираем исчерпанные ресурсы
        # remove resources that have been emptied out
        to_remove = []
        for res in self.cell.resources:
            if res.size <= 0:
                to_remove.append(res)
        for res in to_remove:
            self.cell.resources.remove(res)


@dataclasses.dataclass
class Agent(Entity):
    """
    Нечто, обладающее "эффектами" - уравнениями, которые
    вычисляются в каждую итерацию системы.
    """

    effects: list = field(default_factory=lambda: [])

    # Чтение можно производить только из объектов прошлой итерации,
    # а запись - только в текущую (потому что иначе порядок выполнения)
    # агентов будет влиять на результаты вчислений).
    # Чтобы не возникало путаницы на уровне эффектов, в кждый эффект мы 
    # передаём отдельно объект для чтения (=объект прошлой итерации) и 
    # объект для записи. 
    def do_effects(self, agent_read, cell_write, cell_read, buffer):
        """
        Вызывается каждую итерацию.
        """
        for func in self.effects:
            func(self, agent_read, cell_write, cell_read, buffer)
