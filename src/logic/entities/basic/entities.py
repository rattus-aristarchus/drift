import dataclasses
from dataclasses import fields


@dataclasses.dataclass
class Entity:
    """
    База
    """

    name: str = ""


def inherit_prototype_fields(entity):
    """
    Глубокое копирование сущности, рекурсивно вызывается для
    всех ссылок на другие сущности.

    Этот метод

    !НЕ!

    предназначен для копирования сложных графов объектов; только для
    копирования иерархической сущности, под-сущности которой не ссылаются
    друг на друга.
    """
    copy = type(entity)()

    for field in fields(type(entity)):
        # внутренние поля у копии должны быть свои
        if field.name[0] == '_':
            continue

        value = getattr(entity, field.name)
        new_value = value

        # если прямая ссылка на сущность - вызываем функцию рекурсивно
        if isinstance(value, Entity):
            new_value = inherit_prototype_fields(value)

        # если список - то это может быть список сущностей, тогда
        # рекурсивный вызов для каждого элемента; либо просто список -
        # тогда тупо копируем
        elif isinstance(value, list):
            if len(value) > 0 and isinstance(value[0], Entity):
                new_value = []
                for item in value:
                    new_item = inherit_prototype_fields(item)
                    new_value.append(new_item)
            else:
                new_value = value.copy()

        # если словарь - проверяем, словарь ли сущностей это, и вызываем
        # рекурсивно; если нет, тупо копируем
        elif isinstance(value, dict):
            if len(value) > 0 and isinstance(next(iter(value.values())), Entity):
                new_value = {}
                for key, item in value:
                    new_item = inherit_prototype_fields(item)
                    new_value[key] = new_item
            else:
                new_value = value.copy()


        setattr(copy, field.name, new_value)

    return copy


def get_entity(name, _list):
    for e in _list:
        if e.name == name:
            return e
    return None

def has_entity(name, _list):
    for e in _list:
        if e.name == name:
            return True
    return False
