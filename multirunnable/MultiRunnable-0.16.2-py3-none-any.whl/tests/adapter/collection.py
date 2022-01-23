from multirunnable.adapter.lock import Lock, RLock, Semaphore, BoundedSemaphore
from multirunnable.adapter.communication import Event, Condition
from multirunnable.adapter.collection import FeatureList

import pytest


@pytest.fixture(scope="function", autouse=True)
def reset_collection() -> None:
    _fl = FeatureList()
    _fl.clear()


@pytest.fixture(scope="function")
def feature_list() -> FeatureList:
    return FeatureList()


class TestCollection:

    def test_add(self):
        _feature_collection = None
        _lock = Lock()
        _rlock = RLock()

        try:
            _feature_collection = _lock + _rlock
        except Exception as e:
            assert False, f""
        else:
            assert True, f""
            assert len(_feature_collection) == 2, f""
            assert _feature_collection.index(0) == _lock, f""
            assert _feature_collection.index(1) == _rlock, f""


    def test_append(self, feature_list: FeatureList):
        _lock = Lock()
        _rlock = RLock()

        feature_list.append(_lock)
        feature_list.append(_rlock)

        assert len(feature_list) == 2, f""
        assert feature_list.index(0) == _lock, f""
        assert feature_list.index(1) == _rlock, f""


    def test_insert(self, feature_list: FeatureList):
        _lock = Lock()
        _rlock = RLock()

        feature_list.insert(index=0, value=_lock)
        feature_list.insert(index=0, value=_rlock)

        assert len(feature_list) == 2, f""
        assert feature_list.index(0) != _lock, f""
        assert feature_list.index(0) == _rlock, f""
        assert feature_list.index(1) == _lock, f""


    def test_pop(self):
        _lock = Lock()
        _rlock = RLock()

        _feature_collection = _lock + _rlock
        _feature_collection.pop(0)

        assert len(_feature_collection) == 1, f""
        assert _feature_collection.index(0) != _lock, f""
        assert _feature_collection.index(0) == _rlock, f""


    def test_remove(self):
        _lock = Lock()
        _rlock = RLock()

        _feature_collection = _lock + _rlock
        _feature_collection.remove(_rlock)

        assert len(_feature_collection) == 1, f""
        assert _feature_collection.index(0) != _rlock, f""
        assert _feature_collection.index(0) == _lock, f""


    def test_clear(self, feature_list: FeatureList):
        _lock = Lock()
        _rlock = RLock()

        feature_list.append(_lock)
        feature_list.append(_rlock)
        feature_list.clear()

        assert len(feature_list) == 0, f""


    def test_extend(self, feature_list: FeatureList):
        _other_features_list = FeatureList()
        _other_features_list.clear()

        _lock = Lock()
        _rlock = RLock()
        _smp = Semaphore(value=1)

        feature_list.append(_lock)
        feature_list.append(_rlock)

        _other_features_list.append(_smp)

        assert len(feature_list) == 2, f""
        assert len(_other_features_list) == 1, f""

        feature_list.extend(_other_features_list)

        assert len(feature_list) == 3, f""
        assert feature_list.index(0) != _lock, f""
        assert feature_list.index(1) == _rlock, f""
        assert feature_list.index(2) == _smp, f""


    def test_iterator(self, feature_list: FeatureList):
        _lock = Lock()
        _rlock = RLock()

        feature_list.append(_lock)
        feature_list.append(_rlock)

        _features_iter = feature_list.iterator()

        assert _features_iter.has_next() is True, f""
        while _features_iter.has_next() is True:
            _f = _features_iter.next()
            assert _f is not None, f""
            assert _f == _lock or _f == _rlock, f""

