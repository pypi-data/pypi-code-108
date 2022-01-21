from typing import Dict, List, Callable
import numpy as np
from nwgraph import Node
from ...logger import logger

# Receive a list of arrays (all nodes) and return same list after augmentation without knowing which nodes are what
GeneralPrototype = Callable[ [List[np.ndarray]], List[np.ndarray] ]
# Node specific augmentation. Receive the node itself (for hyperparameters) and the data, return the augmented data
NodeSpecificPrototype = Callable[ [Node, np.ndarray], np.ndarray ]

class NGCAugmentation:
    # @brief General Augmentation module
    # @param[in] nodes The list of all relevant nodes. Data should assume that the received list is using these nodes.
    # @param[in] general_augmentation A list of ordered augmentation callable functions, that are going to be
    #  invariant of all nodes. All nodes are assumed the same (so 2d only should be passed here).
    # @param[in] node_specific_augmentation A dict of node specific augmentation callables. These are called after
    #  the generic ones.
    def __init__(self, nodes: List[Node], general_augmentation: List[GeneralPrototype], \
                 node_specific_augmentation: Dict[str, List[NodeSpecificPrototype]]=None):
        self.node_name_to_node = {node.name: node for node in nodes}
        if node_specific_augmentation is None:
            node_specific_augmentation = {}
        if general_augmentation is None:
            general_augmentation = []

        self.nodes = nodes
        self.general_augmentation = general_augmentation
        self.node_specific_augmentation = node_specific_augmentation
        logger.debug(f"Instantiating {self}")

    def __call__(self, data: Dict[str, np.ndarray]):
        names, values = data.keys(), list(data.values())
        """Call the generic augmentation callbacks for all data at once."""
        for general_fn in self.general_augmentation:
            values = general_fn(values)
        
        nodes = {self.node_name_to_node[name] for name in names}
        result = dict(zip(names, values))

        """Call the node specific augmentation callbacks for each node individually."""
        for name, node_fns in self.node_specific_augmentation:
            node = nodes[name]
            node_value = result[name]
            for node_fn in node_fns:
                node_value = node_fn(node, node_value)
            result[name] = node_value

        return result

    def __str__(self) -> str:
        count_node_specific = {k: len(self.node_specific_augmentation[k]) for k in self.node_specific_augmentation}
        Str = "[Augmentation]"
        Str += f"\n - Nodes: {self.nodes}"
        Str += f"\n - General augmentation functions: {len(self.general_augmentation)}"
        Str += f"\n - Node specific functions: {count_node_specific}"
        return Str
