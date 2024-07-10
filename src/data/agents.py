from src.util import CONST


def add_effects(agent, type, name, get_effect):
    func_names = CONST[type][name]['effects']
    for func_name in func_names:
        effect = get_effect(func_name)
        agent.effects.append(effect)


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

   # def copy_group(self, destination):
    #    new_group = destination.create_group(self.name)
     #   new_group.pops =
        # TODO: allright, this is a really big problem. here we need not the pops
        # in the old group, but the new pops at the new cell
        # maybe this is a sign that my approach with creating a new grid for every turn
        # is wrong
      #  return new_group


class Population(Agent):

    def __init__(self, name):
        super().__init__(name)
        self.group = None
        self.size = 0
        self.age = 0
        self.sapient = False
        if name in CONST['pops']:
            self.sapient = CONST['pops'][name]['sapient']

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


