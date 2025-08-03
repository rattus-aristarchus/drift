import dataclasses
import inspect
from src.logic.entities.basic.entities import Entity
from src.io import models
from src.io.models import Model
from src.logic.entities.basic.recurrents import Recurrent


@dataclasses.dataclass
class SampleEntity(Entity):

    pass

@dataclasses.dataclass
class SampleModel(Model):

    linked_class = SampleEntity

    name: str = ""


def test_create_from_model():
    test_model = SampleModel(name="test")

    test_entity = models.create_from_model(test_model)

    assert test_entity.name == "test"


@dataclasses.dataclass
class SampleClass(Recurrent):

    test_field: str = ""


"""
def test_get_class_members():
    members = SampleClass.__dict__
    print(members)
"""
