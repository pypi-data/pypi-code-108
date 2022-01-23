from tests.utils import PRODUCT, IMPACTS
from hestia_earth.aggregation.utils import _group_by_product, _aggregated_node, _aggregated_version


def test_group_by_product():
    results = _group_by_product(PRODUCT, IMPACTS, ['emissionsResourceUse'], True)
    assert len(results.keys()) == 1

    # non-including organic/irrigated matrix
    results = _group_by_product(PRODUCT, IMPACTS, ['emissionsResourceUse'], False)
    assert len(results.keys()) == 1


def test_aggregated_node():
    node = {'value': 10}
    assert _aggregated_node(node)['aggregated'] is True


def test_aggregated_version():
    node = {'value': 10}
    assert _aggregated_version(node)['aggregated'] == ['value']
