
def has_neighbor_sootnomad(neighbors):
    for next in neighbors:
        nomads = next.get_pop("коптеводы")
        if nomads is not None:
            return True
    return False


def sum_for_cells(pop_name, cells):
    result = 0
    for neighbor in cells:
        pop = neighbor.get_pop(pop_name)
        if pop is not None:
            Logger.debug("found neighboring " + pop.name + ", numbering " + str(pop.size) +
                         " in cell x " + str(neighbor.x) + ", y " + str(neighbor.y))
            result += pop.size
    return result

