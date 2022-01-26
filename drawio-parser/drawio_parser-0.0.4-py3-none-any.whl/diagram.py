from typing import List


class Diagram:
    def __init__(self, name: str, components: List) -> None:
        self.name = name
        self.__components = components
    
    def get_components(self):
        return self.__components