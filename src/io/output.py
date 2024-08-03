import os

from src import util


class Output:

    def __init__(self):
        self.address = util.MAIN_DIR + "/output.csv"
        if os.path.exists(self.address):
            os.remove(self.address)
        open(self.address, "x")

    def write_grid(self, grid):
        for cell in grid.watched_cells:
            self.write_cell(cell)
        self.write_end_of_turn()

    def write_cell(self, cell):
        with open(self.address, "a", encoding="utf-8") as file:
            string = ""
            for pop in cell.pops:
                string += str(pop.size) + ","
            string = string + ","
            file.write(string)

    def write_end_of_turn(self):
        with open(self.address, "a", encoding="utf-8") as file:
            file.write("\n")



