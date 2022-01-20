from overrides import overrides
from .message import Message
from .graph import Graph
from nwmodule.nwmodule import CriterionType

class SimpleGraph(Graph):
	@overrides
	# @brief Send all messages to all possible neighbours.
	def messagePass(self, t: int):
		for edge in self.edges:
			A, B = edge.getNodes()
			for message in A.getMessages():
				y = edge.forward(message.output)
				newMessagePath = [*message.path, edge]
				newMessage = Message(newMessagePath, message.output, y)
				B.addMessage(newMessage)

	@overrides
	# @brief Basic aggregate function. For all messages received in a node, keep a random one.
	def aggregate(self):
		pass

	@overrides
	# @brief Basic criterion function that does the mean of all losses coming from all available edges.
	def getCriterion(self) -> CriterionType:
		def f(edgeLosses):
			L = []
			for edge in edgeLosses:
				l = edgeLosses[edge]
				if len(l) > 0:
					L.append(sum(l) / len(l))
			L = sum(L) / len(L)
			return L
		return f
