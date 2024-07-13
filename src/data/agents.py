
def create_group(model, destination):
    new_group = Group(model.id)
    new_group.effects = list(model.effects)
    destination.groups.append(new_group)
    new_group.territory.append(destination)
    return new_group


def copy_group(group, destination):
    new_group = Group(group.name)
    new_group.effects = list(group.effects)
    destination.groups.append(new_group)
    new_group.territory.append(destination)
    return new_group


def create_pop(model, destination=None):
    # for some unfathomable reason get_pop_effect here is none

    new_pop = Population(model.id)
    new_pop.effects = list(model.effects)
    new_pop.sapient = model.sapient

    if destination:
        destination.pops.append(new_pop)

    return new_pop


def copy_pop(pop, destination):
    new_pop = Population(pop.name)
    new_pop.size = pop.size
    new_pop.age = pop.age
    new_pop.group = pop.group
    new_pop.sapient = pop.sapient
    new_pop.effects = list(pop.effects)
    destination.pops.append(new_pop)
    return new_pop


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
