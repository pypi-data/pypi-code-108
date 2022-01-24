from .data import TigerGraph

__all__ = ["PageRank"]


class BaseFeaturizer:
    def __init__(self, graph: TigerGraph, result_attr: str, timeout: int) -> None:
        self._graph = graph
        self._base_endpoint = "{}:8000/featurize".format(graph.host)
        self._payload = {"graph": graph.graph_name,
                         "result_attr": result_attr, "timeout": timeout}

    def run(self):
        raise NotImplementedError


class PageRank(BaseFeaturizer):
    def __init__(self, graph: TigerGraph, result_attr: str = "pagerank",
                 timeout: int = 16000) -> None:
        super().__init__(graph, result_attr, timeout)
        self._base_endpoint += "/pagerank"
        self._graph._mixed_session.get(
            self._base_endpoint+"/init", params=self._payload)

    def run(self, max_change: float = 0.001, max_iter: int = 25, damping: float = 0.85):
        _params = {"max_change": max_change,
                   "max_iter": max_iter, "damping": damping}
        _params.update(self._payload)
        resp = self._graph._rest_session.get(
            self._base_endpoint+"/run", params=_params)
        resp.raise_for_status()
        return self
