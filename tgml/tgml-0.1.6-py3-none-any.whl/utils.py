from .data import TigerGraph

__all__ = ["split_vertices"]


def split_vertices(graph: TigerGraph, timeout: int = 16000, **split_ratios) -> None:
    assert len(split_ratios) == 3, "Need all train, validation and test ratios"
    assert sum(
        split_ratios.values()) == 1, "Train, validation and test ratios have to sum up to 1"
    endpoint = "{}:8000/split/vertices".format(graph.host)
    _payload = {"graph": graph.graph_name, "timeout": timeout}
    for key, attr, ratio in zip(split_ratios,
                                ("train_mask", "val_mask", "test_mask"),
                                ("train_ratio", "val_ratio", "test_ratio")):
        _payload[attr] = key
        _payload[ratio] = split_ratios[key]
    resp = graph._mixed_session.get(
        endpoint+"/init", params=_payload)
    resp.raise_for_status()
    resp = graph._rest_session.get(
        endpoint+"/run", params=_payload)
    resp.raise_for_status()
