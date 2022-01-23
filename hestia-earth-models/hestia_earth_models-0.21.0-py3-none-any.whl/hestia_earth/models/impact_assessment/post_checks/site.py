from hestia_earth.utils.model import linked_node


def _run(impact: dict): return linked_node(impact.get('site'))


def _should_run(impact: dict):
    site_id = impact.get('site', {}).get('@id')
    run = site_id is not None
    return run


def run(impact: dict): return {**impact, **({'site': _run(impact)} if _should_run(impact) else {})}
