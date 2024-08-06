import dataclasses
import uuid
from src.logic import util
from src.logic.models import Model


@dataclasses.dataclass
class Entity:
    """
    База
    """

    name: str = ""
    model: Model = None


@dataclasses.dataclass
class Recurrent:
    """
    Сущность, копии которой могут существовать в разных
    итерациях модели
    """

    # айдишник, по которому можно опознать копии одной
    # и той же сущности
    id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))
    # при создании новой итерации модели все сущности
    # копируются в нее; last_copy - ссылка на сущность
    # в прошлой итерации; next_copy - ссылка на следующую
    # сущность
    last_copy = None
    next_copy = None

    def on_copy(self, original, all_recurrents):
        return all_recurrents


def relations_list():
    return dataclasses.field(
        default_factory=lambda: [],
        metadata={"type": "relations_list"}
    )


def relations_dict():
    return dataclasses.field(
        default_factory=lambda: {},
        metadata={"type": "relations_dict"}
    )


def deep_copy_list():
    return dataclasses.field(
        default_factory=lambda: [],
        metadata={"type": "deep_copy_list"}
    )


def deep_copy_dict():
    return dataclasses.field(
        default_factory=lambda: {},
        metadata={"type": "deep_copy_dict"}
    )


def copy_recurrent_and_add_to_list(to_copy: Recurrent, all_recurrents):
    """
    """

    copy = dataclasses.replace(to_copy)

    _class = type(to_copy)
    for field in dataclasses.fields(_class):
        old_value = getattr(to_copy, field.name)
        new_value = None

        if field.metadata and 'type' in field.metadata.keys():
            if field.metadata['type'] == "deep_copy_list":
                new_value = []
                for element in old_value:
                    new_value.append(dataclasses.replace(element))

            elif field.metadata['type'] == "deep_copy_dict":
                new_value = {}
                for key, element in old_value.items():
                    new_value[key] = dataclasses.replace(element)

            elif field.metadata['type'] == "relations_list":
                new_value = []
                for recurrent in old_value:
                    recurrent_copy, all_recurrents = _get_or_create_copy(recurrent, all_recurrents)
                    new_value.append(recurrent_copy)

            elif field.metadata['type'] == "relations_dict":
                new_value = {}
                for key, recurrent in old_value.items():
                    recurrent_copy, all_recurrents = _get_or_create_copy(recurrent, all_recurrents)
                    new_value[key] = recurrent_copy

        elif isinstance(old_value, Recurrent):
            new_value, all_recurrents = _get_or_create_copy(old_value, all_recurrents)

        elif isinstance(old_value, Entity):
            new_value = util.copy_dataclass_with_collections(old_value)

        elif isinstance(old_value, list) or isinstance(old_value, dict):
            new_value = old_value.copy()

        if new_value:
            setattr(copy, field.name, new_value)

    all_recurrents[copy.id] = copy
    all_recurrents = copy.on_copy(to_copy, all_recurrents)
    copy.last_copy = to_copy
    to_copy.next_copy = copy

    return copy, all_recurrents


def _get_or_create_copy(element, all_recurrents):
    if element.id in all_recurrents.keys():
        new_copy = all_recurrents[element.id]
    else:
        new_copy, all_recurrents = copy_recurrent_and_add_to_list(element, all_recurrents)

    return new_copy, all_recurrents

