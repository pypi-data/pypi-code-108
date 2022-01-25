from nwgraph import Node, CriterionType
from typing import Dict

class NullNode(Node):
    def __init__(self, **kwargs):
        super().__init__(name="Null", hyperParameters={})

    def getNodeCriterion(self) -> CriterionType:
        return None
    
    def getNodeMetrics(self) -> Dict:
        return {}
