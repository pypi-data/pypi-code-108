# -*- coding: utf-8 -*-

from pip_services3_expressions.tokenizers.utilities.CharReferenceMap import CharReferenceMap


class TestCharReferenceMap:

    def test_default_interval(self):
        map = CharReferenceMap()
        assert map.lookup(ord('A')) is None
        assert map.lookup(0x2045) is None

        map.add_default_interval(True)
        assert map.lookup(ord('A')) is not None
        assert map.lookup(0x2045) is not None

        map.clear()
        assert map.lookup(ord('A')) is None
        assert map.lookup(0x2045) is None

    def test_interval(self):
        map = CharReferenceMap()
        assert map.lookup(ord('A')) is None
        assert map.lookup(0x2045) is None

        map.add_interval(ord('A'), ord('z'), True)
        assert map.lookup(ord('A')) is not None
        assert map.lookup(0x2045) is None

        map.add_interval(0x2000, 0x20ff, True)
        assert map.lookup(ord('A')) is not None
        assert map.lookup(0x2045) is not None

        map.clear()
        assert map.lookup(ord('A')) is None
        assert map.lookup(0x2045) is None

        map.add_interval(ord('A'), 0x20ff, True)
        assert map.lookup(ord('A')) is not None
        assert map.lookup(0x2045) is not None
