from abc import ABC


class Memento(ABC):
    def __init__(self, state: dict):
        self._state = state

    def get_state(self):
        return self._state


class RallyPydanticMemento(Memento):
    def __init__(self, model: dict):
        super().__init__(model)


