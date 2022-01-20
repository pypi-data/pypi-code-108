from pollination.ladybug_comfort.mtx import PmvMtx, AdaptiveMtx, UtciMtx
from queenbee.plugin.function import Function


def test_pmv_mtx():
    function = PmvMtx().queenbee
    assert function.name == 'pmv-mtx'
    assert isinstance(function, Function)


def test_adaptive_mtx():
    function = AdaptiveMtx().queenbee
    assert function.name == 'adaptive-mtx'
    assert isinstance(function, Function)


def test_utci_mtx():
    function = UtciMtx().queenbee
    assert function.name == 'utci-mtx'
    assert isinstance(function, Function)
