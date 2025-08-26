import dataclasses
from dataclasses import field


@dataclasses.dataclass
class World:

    name: str = ""
    width: int = 10
    height: int = 10
    age: int = 0
    mean_temp: float = 7
    # how much the temperature needs to deviate for
    # pops to change by 50%:
    deviation_50: float = 1

    map: str = ""
    # инструкции для наполнения регионов
    cell_instructions: dict = field(default_factory=lambda: {})

    effects: list = field(default_factory=lambda: [])
    structure_effects: list = field(default_factory=lambda: [])
    cell_effects: list = field(default_factory=lambda: [])
    pop_effects: list = field(default_factory=lambda: [])
    res_effects: list = field(default_factory=lambda: [])
