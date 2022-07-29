import util


def write_cell(cell):
    with open(util.MAIN_DIR + "/output.csv", "a", encoding="utf-8") as file:
        string = ""
        for pop in cell.pops:
            string += str(pop.size) + ","
        string = string[:-1] + "\n"
        file.write(string)