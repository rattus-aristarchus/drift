from src.logic.entities.agents.populations import Population
from src.logic.entities.factories import Factory


def test_new():
    factory = Factory()
    pop_prototype = Population(name="test_pop", size=1)
    factory.populations["test_pop"] = pop_prototype

    new_pop = factory.new_population("test_pop")

    assert new_pop
    assert new_pop.size == 1


