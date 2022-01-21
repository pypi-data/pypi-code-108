from abc import abstractmethod
from typing import List
from nwgraph import SimpleEdge

class NGCEdge(SimpleEdge):
    def __init__(self, prefix: str, *args, **kwargs):
        self.prefix = prefix
        super().__init__(*args, **kwargs)

    @abstractmethod
    def getInKeys(self) -> List[str]:
        pass

    def setup(self, **kwargs):
        pass
