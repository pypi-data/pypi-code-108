"""CLI fixtures.

See the `Click testing documentation <https://click.palletsprojects.com/en/7.x/testing/>`__.
"""

from tempfile import NamedTemporaryFile
import pytest
from click.testing import CliRunner


SCRIPT = """
laser l0 P=1
space s1 l0.p1 itm.p1
mirror itm R=0.99 T=0.01 Rc=-0.6
space scav itm.p2 etm.p1 L=1
mirror etm R=&itm.R T=&itm.T phi=&itm.phi Rc=0.6
cav cav1 itm.p2.o
pd pdcav itm.p1.o
"""


@pytest.fixture
def cli():
    """CLI runner for use in tests."""
    return CliRunner()


@pytest.fixture
def isolated_cli(cli):
    """CLI runner for use in tests, with isolated working directory."""
    with cli.isolated_filesystem():
        yield cli


@pytest.fixture
def input_file(tmp_path):
    """A temporary file containing valid kat script."""
    tmpfile = tmp_path / "kat.tmp"
    with open(tmpfile, "w") as fobj:
        fobj.write(SCRIPT)
    yield str(tmpfile)
