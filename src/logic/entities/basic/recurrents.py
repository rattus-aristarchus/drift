"""
Модуль, обеспечивающий копирование сущностей из одной
итерации модели в другую.
"""
import dataclasses
import uuid

from src.logic import util
from src.logic.entities.basic.entities import Entity


@dataclasses.dataclass
class Recurrent:
    """
    Сущность, копии которой могут существовать в разных
    итерациях модели.
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
        """
        Некоторые классы при копировании требуют особой логики
        """
        return all_recurrents


def copy_recurrent_and_add_to_list(to_copy: Recurrent, all_recurrents: dict):
    """
    Скопировать объект Recurrent, а также рекурсивно
    все объекты Recurrent, на которые он ссылается.
    :to_copy: копируемый объект.
    :all_recurrents: словарь уже созданных копий, по их айдишникам. Если на какой-то
    объект есть ссылки в нескольких местах, то при обходе графа объектов
    не должно создаваться несколько отдельных копий такого объекта. Вместо
    этого ссылка должна подставляться на уже созданную копию - которую
    функция находит в all_recurrents по ее айди.
    """

    # вначале - обычное питоновское копирование
    copy = dataclasses.replace(to_copy)
    # добавляем созданную копию в список всех копий
    all_recurrents[copy.name] = copy

    # обходим поля класса, для каждого поля получаем его значение
    for field in dataclasses.fields(type(to_copy)):
        old_value = getattr(to_copy, field.name)
        new_value = None

        # для особых полей выполняем особое копирование
        if field.metadata and 'type' in field.metadata.keys():
            # для полей "deep copy" нужно выполнить глубокое копирование
            # (вместо копирования ссылки)
            if field.metadata['type'] == "deep_copy_list":
                new_value = []
                for element in old_value:
                    new_value.append(dataclasses.replace(element))

            elif field.metadata['type'] == "deep_copy_dict":
                new_value = {}
                for key, element in old_value.items():
                    new_value[key] = dataclasses.replace(element)

            # для полей "relations" нужно вызвать функцию рекурсивно
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

        # если поле - ссылка на единичынй объект Recurrent, его
        # тоже нужно скопировать рекурсивно
        elif isinstance(old_value, Recurrent):
            new_value, all_recurrents = _get_or_create_copy(old_value, all_recurrents)

        # для обычных объектов выполняем просто глубокое копирование
        elif isinstance(old_value, Entity):
            new_value = util.copy_dataclass_with_collections(old_value)

        elif isinstance(old_value, list) or isinstance(old_value, dict):
            new_value = old_value.copy()

        # если в результате одной из предыдущих проверок мы
        # создали новую копию поля, присваиваем ее вместо
        # старого значения
        if new_value:
            setattr(copy, field.name, new_value)

    # выполняем особую логику
    all_recurrents = copy.on_copy(to_copy, all_recurrents)
    # добавляем копиям ссылки друг на друга
    copy.last_copy = to_copy
    to_copy.next_copy = copy
    # цепь ссылок не должна быть бесконечной (для сериализации, и если захотим
    # ограничить количество итераций в памяти). поэтому обнуляем ссылку на пред-предшествующую копию
    if to_copy.last_copy:
        to_copy.last_copy.next_copy = None
        to_copy.last_copy = None

    return copy, all_recurrents


def _get_or_create_copy(element, all_recurrents):
    """
    Метод, который должен обеспечить копию элемента.
    """

    if element.name in all_recurrents.keys():
        # Если элемент уже был скопирован ранее, он будет лежать
        # в all_recurrents, и мы получаем его из этого словаря.
        new_copy = all_recurrents[element.name]
    else:
        # Если нет, создаем новую копию.
        new_copy, all_recurrents = copy_recurrent_and_add_to_list(element, all_recurrents)

    return new_copy, all_recurrents
