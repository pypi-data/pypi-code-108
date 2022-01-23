from abc import ABC


class AbstractInventory(ABC):
    def __init__(self, name="", identifier=""):
        self.namespace = "fml40"
