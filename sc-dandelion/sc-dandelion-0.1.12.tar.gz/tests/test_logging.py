import dandelion as ddl
from subprocess import run


def test_badge():
    p = run(["python", "dandelion/logging/_badge.py"],
            capture_output=True,
            encoding='utf8')
    assert p.returncode == 0
    assert p.stderr == ""
    assert p.stdout != ""
    assert p.stdout.strip('\n') == ddl.__version__


def test_logging():
    ddl.logging.print_header()
    ddl.logging.print_versions()


def test_metadata():
    assert ddl.__email__ is not None
    assert ddl.__author__ is not None
    assert ddl.__classifiers__ is not None
