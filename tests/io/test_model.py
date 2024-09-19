import dataclasses

from src.logic.entities.basic.entities import Entity
from src.io import models
from src.io.models import Model


@dataclasses.dataclass
class TestEntity(Entity):

    pass

@dataclasses.dataclass
class TestModel(Model):

    linked_class = TestEntity

    name: str = ""


def test_create_from_model():
    test_model = TestModel(name="test")

    test_entity = models.create_from_model(test_model)

    assert test_entity.name == "test"
