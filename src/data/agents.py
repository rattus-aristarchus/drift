from src.util import CONST

get_pop_effect = None
get_group_effect = None


class Agent:

    def __init__(self, name):
        self.name = name
        self.effects = []

    def do_effects(self, cell_buffer, grid_buffer):
        pass


class Group(Agent):

    def __init__(self, name):
        super().__init__(name)
        self.pops = []
        # a list of cells
        self.territory = []
        self._add_effects()

    def _add_effects(self):
        func_names = CONST["groups"][self.name]['effects']
        for func_name in func_names:
            effect = get_group_effect(func_name)
            self.effects.append(effect)

    def copy_group_without_pop(self, destination):
        new_group = Group(self.name)
        destination.groups.append(new_group)
        new_group.territory.append(destination)
        return new_group


class Population(Agent):

    def __init__(self, name):
        super().__init__(name)
        self.group = None
        self.size = 0
        self.age = 0
        self.sapient = False
        if name in CONST['pops']:
            self.sapient = CONST['pops'][name]['sapient']
        self._add_effects()

    def _add_effects(self):
        func_names = CONST["pops"][self.name]['effects']
        for func_name in func_names:
            effect = get_pop_effect(func_name)
            self.effects.append(effect)

    def do_effects(self, cell_buffer, grid_buffer):
        for func in self.effects:
            func(self, cell_buffer, grid_buffer)

    def copy_pop(self, destination):
        new_pop = Population(self.name)
        new_pop.size = self.size
        new_pop.age = self.age
        new_pop.group = self.group
        new_pop.sapient = self.sapient
        new_pop.effects = self.effects
        destination.pops.append(new_pop)
        return new_pop


