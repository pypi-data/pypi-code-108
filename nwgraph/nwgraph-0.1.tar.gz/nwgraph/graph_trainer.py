from overrides import overrides
from nwmodule.nwtrainer import NWTrainer
from .edge import Edge

def mean(x, default=0) : return float(sum(x) / len(x)) if len(x) > 0 else default

class GraphTrainer(NWTrainer):
    @overrides
    def callbacksOnIterationEnd(self, data, labels, results, loss, iteration, numIterations, \
        metricResults, isTraining, isOptimizing):

        # Nodes accumulate messages only if part of a graph. A normal edge is just a simple feed forward network with
        #  no special semantics, like message passing.
        def edgeLevelIterationEnd(edge, labels, edgeLosses):
            metrics = edge.getMetrics()
            edgeResult = {k : [] for k in metrics.keys()}
            messages = edge.getNodes()[1].getMessages()
            for message in messages:
                assert len(message.path) > 0
                lastPath = message.path[-1]
                if not isinstance(lastPath, Edge) or lastPath != edge:
                    continue
                for metric in metrics:
                    f = metrics[metric]
                    y = message.output
                    t = labels
                    loss = mean(edgeLosses[edge], default=0)
                    res = f(y, t, loss=loss)
                    edgeResult[metric].append(res)

            # Do the mean of all messages, if any result exists.
            for metric in metrics:
                edgeResult[metric] = mean(edgeResult[metric], default=[])
            return edgeResult

        def nodeLevelIterationEnd(node, labels):
            metrics = node.getNodeMetrics()
            nodeResult = {k : [] for k in metrics}
            messages = node.getMessages()
            for message in messages:
                for metric in metrics:
                    f = metrics[metric]
                    y = message.output
                    t = labels
                    res = f(y, t)
                    nodeResult[metric].append(res)

            # Do the mean of all messages, if any result exists.
            for metric in metrics:
                nodeResult[metric] = mean(nodeResult[metric], default=[])
            return nodeResult

        # Graph level metrics
        metricResults = super().callbacksOnIterationEnd(data, labels, results, loss, iteration, numIterations, \
            metricResults, isTraining, isOptimizing)

        # Edge level metrics
        edgeResults = {}
        for edge in self.model.edges:
            outputNode = edge.outputNode
            if not outputNode.name in labels:
                continue
            edgeLabels = labels[outputNode.name]
            edgeResults[edge] = edgeLevelIterationEnd(edge, edgeLabels, self.model.edgeLosses)
        metricResults["edges"] = edgeResults

        # Node level metrics
        nodeResults = {}
        for node in self.model.nodes:
            if not node.name in labels:
                continue
            nodeLabels = labels[node.name]
            nodeResults[node] = nodeLevelIterationEnd(node, nodeLabels)
        metricResults["nodes"] = nodeResults

        return metricResults

    @overrides
    def epochPrologue(self, epochResults, isTraining:bool):
        res = super().epochPrologue(epochResults, isTraining)
        
        nodeResults, edgeResults = {}, {}
        for edge in self.model.edges:
            X = {}
            for K in epochResults:
                if not edge in epochResults[K]["edges"]:
                    continue
                X[K] = epochResults[K]["edges"][edge]
                for metricName in X[K]:
                    X[K][metricName] = edge.getMetric(metricName).epochReduceFunction(X[K][metricName])
            if len(X) > 0:
                edgeResults[str(edge)] = X
        
        for node in self.model.nodes:
            X = {}
            for K in epochResults:
                if not node in epochResults[K]["nodes"]:
                    continue
                X[K] = epochResults[K]["nodes"][node]
            if len(X) > 0:
                nodeResults[str(node)] = X
        
        res["edges"] = edgeResults
        res["nodes"] = nodeResults
        return res
