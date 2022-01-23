from hestia_earth.utils.model import linked_node


def _run(cycle: dict): return linked_node(cycle.get('site'))


def _should_run(cycle: dict):
    site_id = cycle.get('site', {}).get('@id')
    run = site_id is not None
    return run


def run(cycle: dict): return {**cycle, **({'site': _run(cycle)} if _should_run(cycle) else {})}
