import numpy as np
import torch as tr
import torch.nn as nn
import torch.optim as optim
from abc import abstractmethod
from functools import partial
from copy import copy
from overrides import overrides
from typing import Dict, List, Set, Iterable, Optional
from nwmodule import NWModule

from .draw_graph import drawGraph
from .graph_serializer import GraphSerializer
from .message import Message
from .node import Node
from .edge import Edge
from .logger import logger

# A Graph is a list of Edges. Each edge is a FeedForward network between two nodes.
class Graph(NWModule):
	def __init__(self, edges, hyperParameters={}):
		self.nodes = self.getNodesFromEdges(edges)
		hyperParameters = self.getHyperParameters(hyperParameters, self.nodes, edges)
		super().__init__(hyperParameters=hyperParameters)
		self.edges = nn.ModuleList([edge for edge in edges])

		# (A, B) => Edge(A, B)
		self.edgeLosses = {k : [] for k in self.edges}
		self.serializer = GraphSerializer(model=self)
		self.nameToNodes = {node.name:node for node in self.nodes}

	@overrides
	# trInputs::Dict[str, tr.Tensor]
	# #trLabels::Dict[str, tr.Tensor]
	def networkAlgorithm(self, trInputs, trLabels, isTraining:bool, isOptimizing:bool):
		self.clearLosses()
		logger.debug2("Passing through all the edges for 1 iteration.")
		nodeMessages = self.forward(trInputs, numIterations=1)
		self.edgeLosses, graphLoss = self.graphBackProp(trLabels)
		if isOptimizing:
			self.updateOptimizer(graphLoss, isTraining, isOptimizing)
		return nodeMessages, graphLoss

	def addGTToNodes(self, data):
		# Add potential GT messages, if any.
		for node in self.nodes:
			if not node.name in data:
				continue
			# Both input and output are the same tensor, with the "GT" path. 
			message = Message([f"GT ({node.name})"], data[node.name], data[node.name])
			node.addMessage(message)

	@abstractmethod
	# @brief Method that defines how messages are sent in one iteration.
	def messagePass(self, t: int):
		pass
	
	@abstractmethod
	# @brief Aggregate function must transform all the received messages of a node to one message after all iterations
	#  have been finished. Basically f(node, [message]) = (node, message).
	def aggregate(self):
		pass

	# @brief The forward pass/message passing of a graph. The algorithm is as follows:
	#  - x represents the "external" data of this passing
	#  - each forward call will send all possible messages of each node to all possible neightbours
	#  - x[node] is the new data (if it exists) for this node. Otherwise, only messages from the previous pass are used
	#  - After all the iterations are done, a reduce call is issued, which, for each node reduces the messages to a
	#  potential less number of messages.
	def forward(self, x, numIterations: int = 1):
		self.clearMessages()
		self.addGTToNodes(x)
		for i in range(numIterations):
			self.messagePass(i)
		self.aggregate()
		y = {k: k.getMessages() for k in self.nodes}
		return y

	def graphBackProp(self, trLabels):
		logger.debug2("Computing node losses.")
		edgeLosses = {k:[] for k in self.edges}
		for node in self.nodes:
			for msg in node.getMessages():
				path, _, y = msg.path, msg.input, msg.output
				# GT node, no possible backprop
				if len(path) == 0:
					continue
				# Vote/aggregate node, no possible backprop
				if isinstance(path[-1], str):
					continue
				assert isinstance(path[-1], Edge), path
				edge = path[-1]
				assert edge.getNodes()[1] == node
				# This edge has no criterion, skipping
				if edge.getCriterion() is None:
					continue
				assert node.name in trLabels, f"{node.name} vs {trLabels.keys()}"
				t = trLabels[node.name]
				l = edge.getCriterion()(y, t)
				edgeLosses[edge].append(l)
		logger.debug2("Passed through all nodes.")

		logger.debug2("Computing graph loss.")
		graphLoss = self.getCriterion()(edgeLosses)
		logger.debug2("Computed graph loss.")
		return edgeLosses, graphLoss

	@overrides
	def trainReaderNumSteps(self, reader:Iterable, numSteps:int, numEpochs:int, \
		validationReader:Optional[Iterable]=None, validationNumSteps:int=None):
		from .graph_trainer import GraphTrainer
		return GraphTrainer(self).train(reader, numEpochs, validationReader, numSteps, validationNumSteps)

	def clearMessages(self):
		logger.debug2("Clearing node messages.")
		for node in self.nodes:
			node.clearMessages()

	def getNodeMessages(self) -> List[Message]:
		return {k : k.getMessages() for k in self.nodes}

	def clearLosses(self):
		logger.debug2("Clearing edge losses.")
		# Generic container of all losses for all edges of this graph.
		self.edgeLosses = {k : [] for k in self.edges}

	def getEdges(self) -> List[Edge]:
		edges = []
		for edge in self.edges:
			edges.append(edge)
		return edges

	def getNodes(self) -> List[Node]:
		return self.nodes

	def getNodeByName(self, name: str) -> Node:
		return self.nameToNodes[name]

	def getNodesFromEdges(self, edges:List[Edge]) -> Set[Node]:
		if hasattr(self, "nodes"):
			return self.nodes

		nodes = set()
		nameToNodes = {}
		for edge in edges:
			A, B = edge.getNodes()
			nodes.add(A)
			nodes.add(B)
			if A.name in nameToNodes:
				assert nameToNodes[A.name] == A
			if B.name in nameToNodes:
				assert nameToNodes[B.name] == B
			nameToNodes[A.name] = A
			nameToNodes[B.name] = B
		return nodes

	def draw(self, fileName, cleanup=True, view=False):
		drawGraph(self.nodes, self.edges, fileName, cleanup, view)

	# We also override some methods on the Network class so it works with edges as well.

	@overrides
	def setOptimizer(self, optimizer, **kwargs):
		logger.debug(f"Settings the optimizer '{optimizer}' for all edges. This might overwrite optimizers!")
		# assert isinstance(optimizer, type), "TODO For more special cases: %s" % type(optimizer)
		for edge in self.edges:
			if edge.getNumParams()[1] == 0:
				logger.debug(f"Skipping edge '{edge}' as it has no trainable parameters!")
				continue
			edge.setOptimizer(optimizer, **kwargs)

	@overrides
	def updateOptimizer(self, trLoss, isTraining:bool, isOptimizing:bool, retain_graph=False):
		if trLoss is None:
			return
		if not isTraining or not isOptimizing:
			trLoss.detach_()
			return

		for edge in self.edges:
			if edge.getOptimizer():
				edge.getOptimizer().zero_grad()
		trLoss.backward(retain_graph=retain_graph)
		for edge in self.edges:
			if edge.getOptimizer():
				edge.getOptimizer().step()

	@overrides
	def getOptimizerStr(self):
		strList = super().getOptimizerStr()
		for edge in self.edges:
			strEdge = str(edge)
			if type(edge) == Graph:
				strEdge = "SubGraph"
			edgeStrList = edge.getOptimizerStr()
			strList.extend(edgeStrList)
		return strList

	def getHyperParameters(self, hyperParameters:Dict, nodes:List[Node], edges:List[Edge]) -> Dict:
		# Set up hyperparameters for every node
		hyperParameters = {k : hyperParameters[k] for k in hyperParameters}
		for node in nodes:
			hyperParameters[node.name] = node.hyperParameters
		for edge in edges:
			hyperParameters[str(edge)] = edge.hyperParameters
		return hyperParameters

	def graphStr(self, depth=1):
		Str = "Graph:"
		pre = "  " * depth
		for edge in self.edges:
			if type(edge) == Graph:
				edgeStr = edge.graphStr(depth + 1)
			else:
				edgeStr = str(edge)
			Str += f"\n{pre}-{edgeStr}"
		return Str

	def __str__(self) -> str:
		return self.graphStr()