from typing import List, Dict
from copy import copy
from overrides import overrides
from nwgraph import Edge, Message
from ..edges import SingleLink, TwoHopsNoGT, TwoHopsResidualNoGT, SingleLinkResidual
from ..ngc import NGC
from ...logger import logger

class NGCV1(NGC):
    """This class contains the specific quircks of the current NGC implementation, some of which (but not all):
        - Two types of edges: Single Links and Two Hops no GT
        - Two iterations per forward (1st for SL, 2nd for TH)
        - Two types of nodes: Input Nodes and Output Nodes. Only Input Nodes participate in Single Links.
        - TODO: Others when I recall them
    """
    @staticmethod
    def _getNGCEdgesComplete(nodes: List, inputNodes: List) -> List[List[str]]:
        outputNodes = list(set(nodes).difference(inputNodes))
        allEdges = []
        logger.debug(f"Creating complete graph from nodes: {nodes}. Input nodes: {inputNodes}.")

        # Single links
        for inputNode in inputNodes:
            for outputNode in outputNodes:
                allEdges.append([inputNode, outputNode])

        # Two Hops
        for inputNode in inputNodes:
            for i in range(len(outputNodes)):
                for j in range(i + 1, len(outputNodes)):
                    allEdges.append([inputNode, outputNodes[i], outputNodes[j]])
                    allEdges.append([inputNode, outputNodes[j], outputNodes[i]])

        return allEdges

    def _getNGCEdgesFromList(self, edgesList: List[List[str]]) -> List[Edge]:
        logger.debug(f"Creating edges from a list of edges ({len(edgesList)}).")
        edges = []
        gtKeyToNode = {node.name:node for node in self.nodes}
        singleLinks = {}

        # Pass once to create single links
        for edge in edgesList:
            edgeNodes = [gtKeyToNode[nodeStr] for nodeStr in edge]
            if len(edge) == 2:
                edge = SingleLink(edgeNodes[0], edgeNodes[1])
                key = (edgeNodes[0], edgeNodes[1])
                assert key not in singleLinks
                singleLinks[key] = edge
            elif len(edge) == 3:
                continue
            else:
                assert False
            edges.append(edge)

        # Pass again to create two hops
        for edge in edgesList:
            edgeNodes = [gtKeyToNode[nodeStr] for nodeStr in edge]
            if len(edge) == 2:
                continue
            elif len(edge) == 3:
                key = (edgeNodes[0], edgeNodes[1])
                assert key in singleLinks
                edge = TwoHopsNoGT(singleLinks[key], edgeNodes[1], edgeNodes[2])
            else:
                assert False
            edges.append(edge)
        return edges

    @overrides
    def getNGCEdges(self) -> List[Edge]:
        if self.cfg["edges"] == "complete":
            edges = NGCV1._getNGCEdgesComplete(self.cfg["nodeNames"], self.cfg["inputNodes"])
        else:
            edges = self.cfg["edges"]
        assert isinstance(edges, (list, tuple))
        return self._getNGCEdgesFromList(edges)

    def getSingleLinks(self) -> List[Edge]:
        singleLinks = []
        for edge in self.edges:
            if isinstance(edge, (SingleLink, SingleLinkResidual)):
                singleLinks.append(edge)
        return singleLinks

    def getTwoHops(self) -> List[Edge]:
        twoHops = []
        for edge in self.edges:
            if isinstance(edge, (TwoHopsNoGT, TwoHopsResidualNoGT)):
                twoHops.append(edge)
        return twoHops

    @overrides
    def messagePass(self, t: int):
        assert 0 <= t <= 1
        def isGTMessage(message):
            # GT messages have the following form: ('GT (rgb)',) or ('GT (rgb)', Single Link (rgb -> softseg2)) etc.
            # Basically tuples of paths. Vote messages will "kill" the pathways (though in future/other graph
            #  implementation could allow gradients to flow through the voting path as well).
            return len(message.path) == 1 and isinstance(message.path[0], str) and message.path[0][0 : 2] == "GT"

        def getSingleLinkMessages(edge: Edge, messages: List[Message]) -> List[Message]:
            return list(filter(isGTMessage, messages))

        def getTwoHopsMessages(edge: Edge, messages: List[Message]) -> List[Message]:
            res = []
            for message in messages:
                if isGTMessage(message):
                    continue
                path = message.path[0]
                # GT (rgb) => ["GT", "rgb"]
                GT, node = path.split(" ")
                node = node[1 : -1]
                assert GT == "GT"
                if node != edge.singleLinkNode.name:
                    continue
                res.append(message)
            assert len(res) > 0
            return res

        # Get all messages before doing any propagation so we store the state
        iterationMessages = {node: copy(node.getMessages()) for node in self.nodes}
        for edge in self.edges:
            if isinstance(edge, (SingleLink, SingleLinkResidual)) and t == 1:
                continue
            if isinstance(edge, (TwoHopsNoGT, TwoHopsResidualNoGT)) and t == 0:
                continue

            A, B = edge.getNodes()
            allMessages = iterationMessages[A]
            # for single links, only pass the GT data
            if isinstance(edge, (SingleLink, SingleLinkResidual)):
                validMessages = getSingleLinkMessages(edge, allMessages)
            # for dual hops, only pass the data propagated from a single edge (no gt)
            elif isinstance(edge, (TwoHopsNoGT, TwoHopsResidualNoGT)):
                validMessages = getTwoHopsMessages(edge, allMessages)
            else:
                assert False, f"Unknown type: {type(edge)}"
            # The algorithm for AAAI 2021 paper is computed as such only 1 message is propagated at most due to how
            #  the graph is constructed
            assert len(validMessages) <= len(self.cfg["inputNodes"]), (A, B, validMessages)
            for message in validMessages:
                y = edge.forward(message.output)
                newMessagePath = [*message.path, edge]
                newMessage = Message(newMessagePath, message.output, y)
                B.addMessage(newMessage)

    def forward(self, x):
        # NGC (V1) does only 2 graph iterations: InputNode->XXX (SL) and (InputNode->)XXX->YYY (TH).
        return super().forward(x, numIterations=2)

    def __str__(self):
        Str = super().__str__()
        Str += f"\n  -Input Nodes: {self.cfg['inputNodes']}"
        Str += "\n  -Single links:"
        for edge in filter(lambda edge: isinstance(edge, SingleLink), self.edges):
            Str += f"\n    -{edge}"

        Str += f"\n  -Two Hops (no GT):"
        for edge in filter(lambda edge: isinstance(edge, TwoHopsNoGT), self.edges):
            Str += f"\n    -{edge}"

        return Str