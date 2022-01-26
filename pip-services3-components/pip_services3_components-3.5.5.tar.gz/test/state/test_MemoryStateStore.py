# -*- coding: utf-8 -*-
from pip_services3_components.state import MemoryStateStore
from test.state.StateStoreFixture import StateStoreFixture


class TestMemoryStateStore:
    _cache: MemoryStateStore
    _fixture: StateStoreFixture

    def setup_method(self):
        self._cache = MemoryStateStore()
        self._fixture = StateStoreFixture(self._cache)

    def test_save_and_load(self):
        self._fixture.test_save_and_load()

    def test_delete(self):
        self._fixture.test_delete()
