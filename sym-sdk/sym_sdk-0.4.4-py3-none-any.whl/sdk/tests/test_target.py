import pytest

from sym.sdk.target import AccessTarget


class TestTarget:
    def test_access_target_abstract(self):
        with pytest.raises(TypeError, match="Can't instantiate abstract class AccessTarget"):
            AccessTarget()  # type: ignore
