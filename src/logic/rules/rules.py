import dataclasses


@dataclasses.dataclass
class Rule:

    name: str = ""


@dataclasses.dataclass
class BiomeRule(Rule):

    pass


@dataclasses.dataclass
class ResourceRule(Rule):

    pass


@dataclasses.dataclass
class PopulationRule(Rule):

    pass

