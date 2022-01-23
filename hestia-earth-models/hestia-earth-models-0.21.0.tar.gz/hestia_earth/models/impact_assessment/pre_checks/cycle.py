from hestia_earth.schema import SchemaType

from hestia_earth.models.utils import _load_calculated_node


def _run(impact: dict):
    cycle = _load_calculated_node(impact.get('cycle', {}), SchemaType.CYCLE)
    cycle['site'] = _load_calculated_node(cycle.get('site', {}), SchemaType.SITE)
    return cycle


def _should_run(impact: dict):
    cycle_id = impact.get('cycle', {}).get('@id')
    run = cycle_id is not None
    return run


def run(impact: dict): return {**impact, **({'cycle': _run(impact)} if _should_run(impact) else {})}
