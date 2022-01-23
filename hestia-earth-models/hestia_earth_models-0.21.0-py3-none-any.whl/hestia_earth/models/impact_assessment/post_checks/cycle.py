from hestia_earth.utils.model import linked_node


def _run(impact: dict): return linked_node(impact.get('cycle'))


def _should_run(impact: dict):
    cycle_id = impact.get('cycle', {}).get('@id')
    run = cycle_id is not None
    return run


def run(impact: dict): return {**impact, **({'cycle': _run(impact)} if _should_run(impact) else {})}
