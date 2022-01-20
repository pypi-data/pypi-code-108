import numpy as np
from overrides import overrides
from typing import Dict, Optional
from torch import nn
from torchmetrics import Metric

import torch as tr
import torch.optim as optim

from nwgraph import SimpleGraph as Graph, SimpleEdge as Edge, Node, Message
from nwgraph.node import CriterionType
from nwmodule.pytorch import FeedForwardNetwork
from nwmodule.pytorch.layers import IdentityLayer
from nwmodule.callbacks import SaveModels
from torch.utils.data import Dataset, DataLoader

device = tr.device("cuda") if tr.cuda.is_available() else tr.device("cpu")

class Reader(Dataset):
	def __init__(self, data:Dict[Node, np.ndarray]):
		self.data = data

	def __getitem__(self, index):
		return {
			"data": {
				"A": self.data["A"][index],
				"B": self.data["B"][index],
				"C": self.data["C"][index],
				"D": self.data["D"][index],
			},
			"labels": {
				"E": self.data["E"][index]
			}
		}

	def __len__(self) -> int:
		Keys = list(self.data.keys())
		return len(self.data[Keys[0]])

class Model(FeedForwardNetwork):
	def __init__(self, inDims, outDims):
		super().__init__()
		self.fc = nn.Linear(inDims, outDims)

	def forward(self, x):
		return self.fc(x)

class MyNode(Node):
	def __init__(self, nDims, name):
		self.nDims = nDims
		super().__init__(name)

	@overrides
	def getEncoder(self, outputNode:Optional[Node]=None) -> nn.Module:
		model = Model(inDims=self.nDims, outDims=outputNode.nDims).to(device)
		return model

	@overrides
	def getDecoder(self, inputNode:Optional[Node]=None) -> nn.Module:
		return IdentityLayer().to(device)

	@overrides
	def getNodeMetrics(self) -> Dict[str, Metric]:
		return {}

	@overrides
	def getNodeCriterion(self) -> CriterionType:
		return None


class A(MyNode):
	def __init__(self):
		super().__init__(nDims=5, name="A")

class B(MyNode):
	def __init__(self):
		super().__init__(nDims=7, name="B")

class C(MyNode):
	def __init__(self):
		super().__init__(nDims=10, name="C")

class D(MyNode):
	def __init__(self):
		super().__init__(nDims=6, name="D")

class E(MyNode):
	def __init__(self):
		super().__init__(nDims=3, name="E")

	def getNodeMetrics(self):
		return {"EMetric": lambda y, t, **k: (y - t).abs().mean()}

	def getNodeCriterion(self) -> CriterionType:
		return lambda y, t:((y - t)**2).mean()

class F(E):
	pass

class GraphModelMean(Graph):
	def aggregate(self):
		for node in self.nodes:
			messages = node.getMessages()
			assert len(messages) > 0
			if node.name == "E":
				# Concatenate all messages into one tensor
				trMessages = tr.stack([x.output for x in messages], dim=0)
				# Do mean
				res = trMessages.mean(dim=0)
				oldPath = tuple(x.path for x in messages)
				newPath = [oldPath, "Vote"]
				newMessage = Message(newPath, trMessages, res)
				node.clearMessages()
				node.addMessage(newMessage)

class TestGraph:
	def test_message_passing_1(self):
		MB = 13
		nodes = {A:A(), B:B(), C:C(), D:D(), E:E()}
		edges = [(A, C), (B, C), (C, E), (D, E)]
		edges = [Edge(nodes[a], nodes[b]) for (a, b) in edges]
		graph = Graph(edges).to(device)

		data = {a:tr.randn(MB, nodes[a].nDims).to(device) for a in nodes.keys()}
		X = {nodes[x].name:y for (x, y) in {A:data[A], B:data[B], C:data[C], D:data[D]}.items()}
		T = {nodes[x].name:y for (x, y) in {E:data[E]}.items()}
		expectedOutputShapes = {nodes[x]:y for x, y in {a:data[a].shape for a in data}.items()}
		expectedNumMessages = {nodes[x]:y for x, y in {A:1, B:1, C:3, D:1, E:4}.items()}

		y = graph.npForward(X)
		for node in y:
			numMessages = len(y[node])
			expected = expectedNumMessages[node]
			assert numMessages == expected, "%s: %d vs %d" % (node, numMessages, expected)
			for msg in y[node]:
				path, nodeX, nodeY = msg.path, msg.input, msg.output
				assert nodeY.shape == expectedOutputShapes[node]

	# Same as test_message_passing_1, but uses not F instead of E, which aggregates all messages into 1 by mean
	def test_message_passing_2(self):
		# TODO: Figure this out a bit better, compared to message_passing_1. Do we need a new node? Is not a new 
		#  graph enough?
		MB = 13
		nodes = {A:A(), B:B(), C:C(), D:D(), F:F()}
		edges = [(A, C), (B, C), (C, F), (D, F)]
		edges = [Edge(nodes[a], nodes[b]) for (a, b) in edges]
		graph = GraphModelMean(edges).to(device)

		data = {a:tr.randn(MB, nodes[a].nDims).to(device) for a in nodes.keys()}
		X = {nodes[x].name:y for (x, y) in {A:data[A], B:data[B], C:data[C], D:data[D]}.items()}
		T = {nodes[x].name:y for (x, y) in {F:data[F]}.items()}
		expectedOutputShapes = {nodes[x]:y for x, y in {a:data[a].shape for a in data}.items()}
		expectedNumMessages = {nodes[x]:y for x, y in {A:1, B:1, C:3, D:1, F:1}.items()}

		y = graph.npForward(X)
		for node in y:
			numMessages = len(y[node])
			expected = expectedNumMessages[node]
			assert numMessages == expected, "%s: %d vs %d" % (node, numMessages, expected)
			for msg in y[node]:
				path, nodeX, nodeY = msg.path, msg.input, msg.output
				assert nodeY.shape == expectedOutputShapes[node]

	def test_train_1(self):
		nodes = {A:A(), B:B(), C:C(), D:D(), E:E()}
		edges = [(A, C), (B, C), (C, E), (D, E)]
		edges = [Edge(nodes[a], nodes[b]) for (a, b) in edges]
		graph = Graph(edges).to(device)
		graph.setOptimizer(optim.SGD, lr=0.01)
		print(graph.summary())

		data = {nodes[a].name:np.random.randn(100, nodes[a].nDims).astype(np.float32) for a in nodes}
		reader = DataLoader(Reader(data), batch_size=1)
		graph.addCallback(SaveModels("best", "Loss"))
		graph.trainReader(reader, numEpochs=5)

	def test_metrics_1(self):
		nodes = {A:A(), B:B(), C:C(), D:D(), E:E()}
		edges = [(A, C), (B, C), (C, E), (D, E)]
		edges = [Edge(nodes[a], nodes[b]) for (a, b) in edges]
		graph = Graph(edges).to(device)
		graph.setOptimizer(optim.SGD, lr=0.01)
		data = {nodes[a].name:np.random.randn(100, nodes[a].nDims).astype(np.float32) for a in nodes}
		reader = DataLoader(Reader(data), batch_size=1)
		graph.trainReader(reader, numEpochs=2)
		trainHistory = graph.getTrainHistory()
		assert len(trainHistory) == 2 # 2 epoch
		assert len(trainHistory[0]["Train"]) == 4 # 1 graph level metric: Loss, 1 duration, 1 edges, 1 nodes metrics
		assert len(trainHistory[0]["edges"]) == 2 # 2 edges that have metrics: C->E and D->E
		assert len(trainHistory[0]["nodes"]) == 1 # 1 node that has metrics: E

if __name__ == "__main__":
	# TestGraph().test_message_passing_2()
	TestGraph().test_train_1()
	# TestGraph().test_metrics_1()
	pass