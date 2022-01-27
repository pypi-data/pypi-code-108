from abc import abstractmethod


class Operator:
    def __init__(self, *logic):
        self.logics = logic

    @abstractmethod
    def __bool__(self):
        pass


class Or(Operator):
    def __bool__(self):
        return any(self.logics)


class And(Operator):
    def __bool__(self):
        return all(self.logics)


class Not(Operator):
    def __bool__(self):
        return not self.logics
