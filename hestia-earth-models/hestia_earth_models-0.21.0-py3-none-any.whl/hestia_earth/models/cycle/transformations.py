from hestia_earth.utils.tools import flatten


def _emissions(transformation: dict):
    emissions = transformation.get('emissions', [])
    inputs = [transformation.get('term')]
    should_run = len(transformation.get('inputs', [])) > 0
    return [{**e, 'inputs': inputs} for e in emissions] if should_run else []


def run(cycle: dict): return flatten(list(map(_emissions, cycle.get('transformations', []))))
