from chaosreliably import __version__, discover


def test_that_discover_returns_correct_discovery() -> None:
    discovery = discover()
    assert discovery["extension"]["name"] == "chaostoolkit-reliably"
    assert discovery["extension"]["version"] == __version__
    names = [activity["name"] for activity in discovery["activities"]]
    assert len(names) == 3
    for name in [
        "get_objective_results_by_labels",
        "slo_is_met",
        "all_objective_results_ok",
    ]:
        assert name in names
