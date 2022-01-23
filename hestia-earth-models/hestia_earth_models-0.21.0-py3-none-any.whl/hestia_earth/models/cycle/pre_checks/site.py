from hestia_earth.schema import SchemaType

from hestia_earth.models.utils import _load_calculated_node


def _run(cycle: dict): return _load_calculated_node(cycle.get('site', {}), SchemaType.SITE)


def _should_run(cycle: dict):
    site_id = cycle.get('site', {}).get('@id')
    run = site_id is not None
    return run


def run(cycle: dict): return {**cycle, **({'site': _run(cycle)} if _should_run(cycle) else {})}
