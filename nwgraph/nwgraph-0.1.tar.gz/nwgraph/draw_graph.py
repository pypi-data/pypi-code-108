from graphviz import Digraph
# from neural_wrappers.graph import Graph, Edge

class GraphDrawer:
	def __init__(self, nodes, edges):
		self.nodes = nodes
		self.edges = edges

		# Convert the names into basic ones, labeled by a string digit
		self.mapNodes = {nodes[i] : str(i) for i in range(len(nodes))}
		# self.dotEdges = self.getEdgesStr()

	# def getEdgesStr(self):
	# 	dotEdges = []
	# 	for i in range(len(self.edges)):
	# 		edge = self.edges[i]
	# 		print(type(edge) == Graph)
	# 		print(type(edge) == Edge)
	# 		breakpoint()
	# 		A, B = edge.inputNode, edge.outputNode
	# 		dotA, dotB = self.mapNodes[A], self.mapNodes[B]
	# 		dotEdges.append("%s%s" % (dotA, dotB))
	# 	return dotEdges

	def getDot(self):
		dot = Digraph(format="png", engine="fdp")
		# Each node also has a subgraph for other stuff, like GT box or edge networks
		subgraphs = {}
		for node in self.nodes:
			dot.node(name=self.mapNodes[node], label=node.name, shape="oval")
			subgraphs[node] = Digraph()

		# Add basic edges
		for i in range(len(self.edges)):
			edge = self.edges[i]
			# for node in edge.getNodes():
			if hasattr(edge, "inputNode"):
				A, B = edge.inputNode, edge.outputNode
				dot.edge(self.mapNodes[A], self.mapNodes[B], len="2.0", label="  %d  " % (i + 1))
			else:
				pass

		# Add GT edges
		# for node in self.nodes:
		# 	if not node.groundTruthKey:
		# 		continue
		# 	subgraphs[node].node(name="cluster_GT-%s" % (self.mapNodes[node]), label="GT", shape="box", width="0.3")
		# 	subgraphs[node].edge("cluster_GT-%s" % (self.mapNodes[node]), self.mapNodes[node], len="0.5", orientation="90")

		for node in self.nodes:
			dot.subgraph(subgraphs[node])
		return dot

	# TODO: edge-edge is only supported (Add node-edge, edge-node, node-node edge types)
	def draw(self, fileName, cleanup, view):
		# Create the graph using the original labels
		dot = self.getDot()
		dot.render(fileName, view=view, cleanup=cleanup)

def drawGraph(nodes, edges, fileName, cleanup, view):
	GraphDrawer(list(nodes), list(edges)).draw(fileName, cleanup, view)