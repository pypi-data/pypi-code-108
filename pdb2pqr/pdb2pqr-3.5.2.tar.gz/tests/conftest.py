"""Configure PDB2PQR test suite."""
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-long", action="store_true", default=False, help="run long tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "long: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-long"):
        # --run-long given in cli: do not skip long tests
        return
    skip_long = pytest.mark.skip(reason="need --run-long option to run")
    for item in items:
        if "long_test" in item.keywords:
            item.add_marker(skip_long)
