
class SROMGraph(object):
    
    @property
    def stages(self):
        return self._stages

    @property
    def paths(self):
        return self._paths

    @paths.setter
    def paths(self, value):
        self._paths = value

    @property
    def digraph(self):
        return self._graph

    @property
    def number_of_nodes(self):
        return self._graph.number_of_nodes()

    @property
    def number_of_edges(self):
        return self._graph.number_of_edges()
