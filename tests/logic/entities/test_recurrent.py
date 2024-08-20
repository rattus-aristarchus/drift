import dataclasses

import src.logic.entities.basic.custom_fields
from src.logic.entities.agents.populations import Population, Need
from src.logic.entities.basic import recurrents
from src.logic.entities.cells import Cell, Biome
from src.logic.entities.basic.entities import Entity
from src.logic.entities.basic.recurrents import Recurrent
from src.logic.entities.agents.structures import Structure
from src.logic.models.models import NeedModel


@dataclasses.dataclass
class TestRecurrent0(Recurrent):

    mutual_reference: list = src.logic.entities.basic.custom_fields.relations_list()


@dataclasses.dataclass
class TestRecurrent1(Recurrent):

    mutual_reference: list = src.logic.entities.basic.custom_fields.relations_list()


def test_copy_mutual_reference():
    recurrent_0 = TestRecurrent0()
    recurrent_1 = TestRecurrent1()
    recurrent_0.mutual_reference.append(recurrent_1)
    recurrent_1.mutual_reference.append(recurrent_0)

    copy_0, all_recurrents = recurrents.copy_recurrent_and_add_to_list(recurrent_0, {})

    # проверяем, что у нас по взаимной ссылке метод не был выполнен
    # для первоначального объекта по второму разу
    assert len(all_recurrents) == 2


@dataclasses.dataclass
class TestClass(Recurrent):

    deep_list: list = src.logic.entities.basic.custom_fields.deep_copy_list()
    deep_dict: dict = src.logic.entities.basic.custom_fields.deep_copy_dict()


def test_deep_copy_list_element_is_different():
    test_obj = TestClass()
    test_ent = Entity(name="unchanged")
    test_obj.deep_list.append(test_ent)

    copy, all_recurrents = recurrents.copy_recurrent_and_add_to_list(test_obj, {})
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
    copy_pop, all_recurrents = recurrents.copy_recurrent_and_add_to_list(pop, {})
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
    copy, all_recurrents = recurrents.copy_recurrent_and_add_to_list(cell, {})
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
