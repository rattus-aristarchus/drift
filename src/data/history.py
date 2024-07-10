from src.data import grid
from src.data.grid import Grid


class History:

    def __init__(self, world_width, world_height):
        self.past_grids = []
        self.turn = 0
        self.width = world_width
        self.height = world_height
        first_grid = Grid(world_width, world_height, self)
        grid.populate(first_grid)
        self.past_grids.append(first_grid)

    def new_turn(self):
        """
        Create a new grid for the new turn.
        """
        self.turn += 1
        old_grid = self.past_grids[-1]
        new_grid = grid.copy(old_grid)
        grid.increase_age(new_grid)
        self.past_grids.append(new_grid)
        return new_grid

    def current_state(self):
        return self.past_grids[-1]

    def state_at_turn(self, turn):
        if turn < len(self.past_grids):
            return self.past_grids[turn]
        else:
            return None
