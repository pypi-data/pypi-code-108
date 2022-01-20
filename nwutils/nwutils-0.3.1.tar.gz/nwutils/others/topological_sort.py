from typing import Dict, List, T

# Given a graph as a dict {Node : [Dependencies]}, returns a list [Node] ordered with a correct topological sort order
# Applies Kahn's algorithm: https://ocw.cs.pub.ro/courses/pa/laboratoare/laborator-07
def topologicalSort(depGraph:Dict[T, List[T]]) -> List[T]:
	L, S = [], []

	# First step is to create a regular graph of {Node : [Children]}
	graph = {k : [] for k in depGraph.keys()}
	inNodesGraph = {}
	for key in depGraph:
		for parent in depGraph[key]:
			assert parent in graph, "Node '%s' is not in given graph: %s" % (parent, graph.keys())
			graph[parent].append(key)
		# Transform the depGraph into a list of number of in-nodes
		inNodesGraph[key] = len(depGraph[key])
		# Add nodes with no dependencies and start BFS from them
		if inNodesGraph[key] == 0:
			S.append(key)

	while len(S) > 0:
		u = S.pop()
		L.append(u)

		for v in graph[u]:
			inNodesGraph[v] -= 1
			if inNodesGraph[v] == 0:
				S.append(v)

	for key in inNodesGraph:
		if inNodesGraph[key] != 0:
			raise Exception("Graph is not acyclical")
	return L