import util


class Output:

    def __init__(self):
        self.address = util.MAIN_DIR + "/output.csv"

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
