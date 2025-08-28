from src.logger import CustomLogger

logger = CustomLogger(__name__)

"""
В этом модуле описывается максимально абстрактная логика последовательности
вычислений. Здесь не должно быть ничего, связанного с сутью моделей (условно, 
эта логика должна быть применима и к биологическим эмуляциям, и к историческим).
"""


class Buffer:

    def __init__(self, world):
        self.world = world
        self.memory = {}



class GridCPU:
    """
    Главный класс, заведующий выполнением алгоритмов модели
    """

    def __init__(self, world, create_intermediate_grid):
        self.grid = None
        self.cpus = []
        self.world = world
        self._create_intermediate_grid = create_intermediate_grid

        self.effects = world.effects
        self.structure_effects = world.structure_effects
        self.relation_effects = world.relation_effects
        self.pop_effects = world.pop_effects
        self.res_effects = world.res_effects
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

        # вначале общие алгоритмы, которые одинаковы для всех сущностей
        first = True
        for func in self.effects:
            if first:
                first = False
            else:
                self.grid = self._create_intermediate_grid()
            func(self.grid, self.grid.last_copy, buffer)

        self._grid_level_messages(buffer)

        for func in self.structure_effects:
            self.grid = self._create_intermediate_grid()
            for structure in self.grid.structures:
                if structure.last_copy:
                    func(structure, structure.last_copy, buffer)

        for func in self.relation_effects:
            self._traverse_grid_with_effect(func, "structures", buffer)
        for func in self.pop_effects:
            self._traverse_grid_with_effect(func, "pops", buffer)
        for func in self.res_effects:
            self._traverse_grid_with_effect(func, "resources", buffer)

        # затем алгоритмы, которые могут отличаться у разных сущностей одного вида
        for structure in self.grid.structures:
            structure.do_effects(None, None, None, buffer)

        # передаем выполнение управляющим объектам для отдельных клеток
        self.refresh_cpus(self.grid)
        for cell_cpu in self.cpus:
            cell_cpu.do_effects(buffer, self.cell_effects)


    def _traverse_grid_with_effect(self, effect, entity_list_name, buffer):
        self.grid = self._create_intermediate_grid()
        for cell in self.grid.cells_as_list():
            for recurrent in eval(f"cell.{entity_list_name}"):
                if recurrent.age > 0:
                    effect(recurrent, recurrent.last_copy, cell, cell.last_copy, buffer)


    def _grid_level_messages(self, buffer):
        temp = round(self.grid.state.temperature, 3)
        msg = (f"The age is {self.grid.state.age}. Global temperature"
                f" is {temp}.")
        if "temp_deviation" in buffer.memory.keys():
            dev = round(buffer.memory["temp_deviation"], 3)
            msg += (f" It deviates from"
                    f" mean by {dev}.")
        logger.info(msg)



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

        recurrent_agents = self.cell.structures + self.cell.pops + self.cell.resources

        for agent in recurrent_agents:
            # если возраст нулевой, агент
            # был создан в эту итерацию, и вычислять его эффекты
            # не нужно
            if agent.age > 0:
                agent.do_effects(agent.last_copy, self.cell, self.cell.last_copy, buffer)

        # алгоритмы для рынков
        for market in self.cell.markets:
            market.do_effects(None, self.cell, self.cell.last_copy, buffer)

        self._garbage_collection()

    def _garbage_collection(self):
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