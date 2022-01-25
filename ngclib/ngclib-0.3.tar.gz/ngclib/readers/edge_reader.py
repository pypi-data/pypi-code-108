import numpy as np
from overrides import overrides
from typing import List, Union, Dict
from nwgraph import Edge, Node
from .ngc_npz_reader import NGCNpzReader
from .augmentation import NGCAugmentation, GeneralPrototype, NodeSpecificPrototype, get_augmentation

# Reader used to train a single edge at a time. For now this reader takes the original reader (with all possible gtKeys
#  for the graph) and only sends the data and labels required for this particular edge. We assume that edges only need
#  an input. More complicated edges might need additional readers.
class EdgeReader(NGCNpzReader):
	def __init__(self, path, nodes: List[Node], edge: Edge, inKeys: Union[Node, List[Node]], \
				 general_augmentation: List[GeneralPrototype]=None, \
                 node_specific_augmentation: Dict[str, List[NodeSpecificPrototype]]=None):
		if isinstance(inKeys, str):
			inKeys = [inKeys]
		# We only care about all input keys of the edge plus the output node of the edge (for gt)
		node_name_to_node = {node.name: node for node in nodes}
		gt_node = node_name_to_node[edge.outputNode.name]
		relevant_node_names = [*inKeys, edge.outputNode.name]
		relevant_nodes = [node_name_to_node[x] for x in relevant_node_names]
	
		self.augmentation = NGCAugmentation(relevant_nodes, general_augmentation, node_specific_augmentation)
		super().__init__(path=path, nodes=relevant_nodes, gtNodes=[gt_node])
		self.edge = edge
		self.inKeys = inKeys

	@overrides
	def mergeFn(self, x):
		"""EdgeReader will not behave like the graph reader. Data is given as a dict, while labels as a regular
		array. Edges will have to understand this format for training.
		"""
		res = super().mergeFn(x)
		all_nodes_data = res["data"]
		all_nodes_data = self.augmentation(all_nodes_data)
		data = {k: all_nodes_data[k] for k in self.inKeys}
		labels = all_nodes_data[self.edge.outputNode.name]
		return {"data": data, "labels": labels}

	def __str__(self) -> str:
		A, B = self.edge.getNodes()
		Type = str(type(self.edge)).split(".")[-1][0 : -2]
		Str = f"[EdgeReader] {A}->{B} (Edge Type: {Type} inKeys: {self.inKeys})"
		Str += super().__str__()
		return Str
