import dataclasses

from src.logic.entities import entities, cells
from src.logic.entities.agents import Population, Need
from src.logic.entities.cells import Cell, Biome
from src.logic.entities.entities import Entity, Recurrent
from src.logic.entities.grids import Grid
from src.logic.entities.structures import Structure
from src.logic.models import NeedModel


@dataclasses.dataclass
class TestClass(Recurrent):

    deep_list: list = entities.deep_copy_list()
    deep_dict: dict = entities.deep_copy_dict()


def test_deep_copy_list_element_is_different():
    test_obj = TestClass()
    test_ent = Entity(name="unchanged")
    test_obj.deep_list.append(test_ent)

    copy, all_recurrents = entities.copy_recurrent_and_add_to_list(test_obj, {})
    copy.deep_list[0].name = "changed"

    assert test_ent.name == "unchanged"
    assert len(all_recurrents) == 1


def test_copy_pop_is_different():
    sample_cell = Cell(x=0, y=0)
    pop = Population(name="test_pop")
    test_need = Need(
        name="test_need",
        per_1000=50
    )
    test_need.model = NeedModel(id="test_need_model")
    test_need_1 = Need(name="test_need_1")
    test_need_1.model = NeedModel(id="test_need_model_1")
    pop.needs.append(test_need)
    sample_cell.pops.append(pop)

    pop.size = 5

#    copy_pop = agents.copy_pop_without_owned(pop, sample_cell)
    copy_pop, all_recurrents = entities.copy_recurrent_and_add_to_list(pop, {})
    copy_pop.needs.append(test_need_1)
    copy_pop.size += 1
    copy_pop.get_need(need_id="test_need_model").per_1000 = 60

    assert pop.size == 5
    assert len(pop.needs) == 1
    assert pop.get_need(need_id="test_need_model").per_1000 == 50


def test_copy_cell_is_different():
    # arrange
    cell = Cell(x=0, y=0)
    pop = Population(name="test_pop")
    cell.pops.append(pop)
    test_struct = Structure(name="old_structure")
    test_biome = Biome()
    test_biome.capacity["test_pop"] = 1
    cell.get_pop("test_pop").size = 5
#    cell_with_pop.get_pop("test_pop").structures.append(test_struct)
    cell.structures.append(test_struct)
    cell.biome = test_biome

    # act
#    copy = cells.copy_cell_without_structures(cell_with_pop)
    copy, all_recurrents = entities.copy_recurrent_and_add_to_list(cell, {})
    copy.structures[0].name = "new_structure"
    copy.get_pop("test_pop").size += 1
    copy.biome.capacity["test_pop"] += 1

    # make sure originals haven't changed
    assert cell.get_pop("test_pop").size == 5
    assert copy.get_pop("test_pop").size == 6
  #  assert len(copy.get_pop("test_pop").structures) > 0
    assert cell.structures[0] == test_struct
    assert test_biome.capacity["test_pop"] == 1


"""
def test_copy_transfers_territory():

    old_cell = Cell(
        name="old_cell",
        x=0,
        y=0
    )
    new_cell = cells.copy_cell_without_structures(old_cell)
    new_cell.name = "new_cell"
    new_grid = Grid()
    new_grid.cells = {0: {0: new_cell}}
    structure = Structure()
    structure.territory.append(old_cell)

#    new_structure = structures.copy_structure(structure, grid=new_grid)
    new_structure, all_recurrents = entities.copy_recurrent_and_add_to_list(
        structure,
        {new_cell.id: new_cell}
    )

    assert len(new_structure.territory) == 1
    assert new_structure.territory[0] == new_cell
"""
