import pytest

from sym.sdk.flow import Flow, Run


class TestFlow:
    def test_flow_abstract(self):
        with pytest.raises(TypeError, match="Can't instantiate abstract class Flow"):
            Flow()  # type: ignore

    def test_run_abstract(self):
        with pytest.raises(TypeError, match="Can't instantiate abstract class Run"):
            Run()  # type: ignore
