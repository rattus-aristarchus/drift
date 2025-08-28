import dataclasses
from dataclasses import field
from src.logic.entities.basic import custom_fields, entities
from src.logic.entities.basic.entities import Entity
from src.logic.entities.basic.recurrents import Recurrent
from src.logger import CustomLogger
from src.logic.entities.biomes import Biome

logger = CustomLogger(__name__)


@dataclasses.dataclass
class Cell(Entity, Recurrent):
    """
    Клетка карты.
    """

    x: int = 0
    y: int = 0
    neighbors: list = custom_fields.relations_list()

    markets: list = field(default_factory=lambda: [])
    pops: list = custom_fields.relations_list()
    structures: list = custom_fields.relations_list()
    resources: list = custom_fields.relations_list()
    biome: Biome = None

    # словарь имя популяци / привлекательность для миграции
    # или социального лифта
    draw: dict = field(default_factory=lambda: {})
    # трудность миграции / социального лифта
    barrier: dict = field(default_factory=lambda: {})


    def on_copy(self, original, all_recurrents):
        # рынкам ничего от прошлой итерации сохранять не нужно
        self.markets = []
        return all_recurrents

    def get_pop(self, name):
        return entities.get_entity(name, self.pops)

    def get_res(self, name):
        return entities.get_entity(name, self.resources)

    def has_res_type(self, type):
        for res in self.resources:
            if res.type == type:
                return True
        return False

    def add_territory(self, structure):
        if structure not in self.structures:
            self.structures.append(structure)
        if self not in structure.territory:
            structure.territory.append(self)

    def _find_structure(self, name):
        for group in self.structures:
            if group.name == name:
                return group
        return None

    def increase_age_for_everything(self, value=1):
        recurrents = [self] + self.pops + self.resources + self.structures

        for recurrent in recurrents:
            recurrent.age += value


def create_cell(x, y, biome_name, factory):
    result = Cell(x=x, y=y)
    biome = factory.new_biome(biome_name)
    if biome is None:
        logger.error(f"Trying to create cell with invalid biome name: {biome}")
    else:
        result.biome = biome
    logger.debug(f"Creating cell at ({str(x)},{str(y)}) with biome {biome_name}")
    for res_name, size in biome.starting_resources:
        resource = factory.new_resource(res_name, result)
        resource.size = size
        logger.debug(f"Adding {str(size)} of resource {res_name}")
    return result
