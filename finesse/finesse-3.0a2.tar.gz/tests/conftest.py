"""Test fixtures shared by all tests."""

import pytest


def pytest_addoption(parser):
    # Add an option to change the Hypothesis max_examples setting.
    parser.addoption(
        "--hypothesis-max-examples",
        action="store",
        default=None,
        help="set the Hypothesis max_examples setting",
    )


def pytest_configure(config):
    # Set Hypothesis max_examples.
    hypothesis_max_examples = config.getoption("--hypothesis-max-examples")
    if hypothesis_max_examples is not None:
        import hypothesis

        hypothesis.settings.register_profile(
            "hypothesis-overridden", max_examples=int(hypothesis_max_examples)
        )

        hypothesis.settings.load_profile("hypothesis-overridden")


@pytest.fixture(autouse=True)
def test_setup_and_teardown():
    """Fixture that runs before and after all tests."""
    from finesse.config import autoconfigure
    from finesse.datastore import invalidate

    # Reset to default configuration.
    autoconfigure()

    # Run the test.
    yield

    # Delete the global cache.
    invalidate()
