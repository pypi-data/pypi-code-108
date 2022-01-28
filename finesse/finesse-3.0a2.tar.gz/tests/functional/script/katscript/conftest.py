import pytest
from finesse.script.spec import KatSpec

# The fixtures below have package scope because the tests in this directory should not
# try to modify the spec or compiler in any way. Tests that modify the spec or compiler
# should go elsewhere.


@pytest.fixture(scope="package")
def spec():
    return KatSpec()
