# -*- coding: utf-8 -*-
from pip_services3_components.state import IStateStore

KEY1: str = "key1"
KEY2: str = "key2"

VALUE1: str = "value1"
VALUE2: str = "value2"


class StateStoreFixture:
    _state: IStateStore = None

    def __init__(self, state: IStateStore):
        self._state = state

    def test_save_and_load(self):
        self._state.save(None, KEY1, VALUE1)
        self._state.save(None, KEY2, VALUE2)

        val = self._state.load(None, KEY1)
        assert val is not None
        assert VALUE1 == val

        values = self._state.load_bulk(None, [KEY2])
        assert len(values) == 1
        assert KEY2 == values[0].key
        assert VALUE2 == values[0].value

    def test_delete(self):
        self._state.save(None, KEY1, VALUE1)

        self._state.delete(None, KEY1)

        val = self._state.load(None, KEY1)
        assert val is None
