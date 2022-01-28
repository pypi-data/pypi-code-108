"""Legacy parser gauss command tests."""

import pytest


def test_nonexistent_node_invalid(parser):
    """
    Test that creating a gauss command with a component/node that
    doesn't exist throws an error.

    See #221.
    """
    with pytest.raises(Exception):
        parser.parse(
            """
            l laser 2.5 0.0 0.0 n1
            s s1 1 n1 n2
            m m1 0 1 0 n2 n3
            gauss g1 l1 n2 1 10
            noxaxis
            """
        )
