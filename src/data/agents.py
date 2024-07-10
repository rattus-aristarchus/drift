from src.util import CONST

get_pop_effect = None
get_group_effect = None


def create_group(name, destination, get_effect=get_group_effect):
    new_group = Group(name)
    _add_group_effects(new_group)
    destination.groups.append(new_group)
    new_group.territory.append(destination)
    return new_group


def create_pop(name, destination=None, get_effect=get_pop_effect):
    # for some unfathomable reason get_pop_effect here is none

    new_pop = Population(name)
    _add_pop_effects(new_pop)

    if name in CONST['pops']:
        new_pop.sapient = CONST['pops'][name]['sapient']

    if destination:
        destination.pops.append(new_pop)

    return new_pop


def copy_pop(pop, destination):
    new_pop = Population(pop.name)
    new_pop.size = pop.size
    new_pop.age = pop.age
    new_pop.group = pop.group
    new_pop.sapient = pop.sapient
    new_pop.effects = pop.effects
    destination.pops.append(new_pop)
    return new_pop


def _add_group_effects(group):
    func_names = CONST["groups"][group.name]['effects']
    for func_name in func_names:
        effect = get_group_effect(func_name)
        group.effects.append(effect)


def _add_pop_effects(pop):
    func_names = CONST["pops"][pop.name]['effects']
    for func_name in func_names:
        effect = get_pop_effect(func_name)
        pop.effects.append(effect)


class Agent:

    def __init__(self, name):
        self.name = name
        self.effects = []

    def do_effects(self, cell_buffer, grid_buffer):
        for func in self.effects:
            func(self, cell_buffer, grid_buffer)


class Group(Agent):

    def __init__(self, name):
        super().__init__(name)
        self.pops = []
        # a list of cells
        self.territory = []


class Population(Agent):

    def __init__(self, name):
        super().__init__(name)
        self.group = None
        self.size = 0
        self.age = 0
        self.sapient = False
