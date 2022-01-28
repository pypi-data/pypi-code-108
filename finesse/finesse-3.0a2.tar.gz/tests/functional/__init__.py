import pytest

# Register util module assertion error rewriting.
# NOTE: this needs to happen before util is actually imported by any other test code.
pytest.register_assert_rewrite(f"{__name__}.diff")
