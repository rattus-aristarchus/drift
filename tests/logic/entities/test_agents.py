import dataclasses

import pytest

from src.logic.entities.agents import ownership
from src.logic.entities.agents.populations import Population
from src.logic.entities.agents.resources import Resource
from src.logic.entities.basic import entities
from src.logic.entities.basic.entities import Entity
from src.logic.entities.basic.recurrents import Recurrent


def sample_effect():
    return "effect executed"


owned_vs_free = [
    (100, 0),
    (100.1, 0),
    (-1, 100)
]


@pytest.mark.parametrize("owned,free", owned_vs_free)
def test_resource_get_free_amount_corner_cases(owned, free):
    res = Resource(
        size=100
    )
    res.owners["test_owner"] = owned

    assert res.get_free_amount() == free


def test_set_ownership_to_zero():
    pop = Population(
        name="test_pop"
    )
    res = Resource()
    pop.owned_resources.append(res)
    res.owners[pop.name] = 100

    ownership.set_ownership(pop, res, 0)

    assert len(pop.owned_resources) == 0
    assert len(res.owners) == 0


def test_set_ownership_to_full():
    pop = Population(
        name="test_pop"
    )
    res = Resource(
        size=100
    )

    ownership.set_ownership(pop, res)

    assert len(pop.owned_resources) == 1
    assert len(res.owners) == 1
    assert pop.name in res.owners.keys()
    assert res.owners["test_pop"] == 100



@dataclasses.dataclass
class TestSubEntity(Entity):
    pass

@dataclasses.dataclass
class TestEntity:

    sub_entity: TestSubEntity = None
    sub_entity_list: list = dataclasses.field(default_factory=lambda: [])


def test_inherit_prototype_fields_copies_sub_entity():
    test = TestEntity()
    sub = TestSubEntity()
    sub_1 = TestSubEntity()
    test.sub_entity = sub
    test.sub_entity_list.append(sub_1)

    copy = entities.inherit_prototype_fields(test)
    sub.name = "changed"
    sub_1.name = "changed"

    assert copy.sub_entity
    assert isinstance(copy.sub_entity, TestSubEntity)
    assert copy.sub_entity.name == ""
    assert len(copy.sub_entity_list) == 1
    assert isinstance(copy.sub_entity_list[0], TestSubEntity)
    assert copy.sub_entity_list[0].name == ""

@dataclasses.dataclass
class EntityWithId(Recurrent):

    pass

def test_inherit_prototype_fields_ignores_id():
    test_entity = EntityWithId()

    copy = entities.inherit_prototype_fields(test_entity)

    assert copy._id != test_entity._id
