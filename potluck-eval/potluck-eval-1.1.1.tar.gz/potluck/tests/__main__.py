"""
Runs tests via pytest. Invoke using `python -m potluck.tests`.

tests/__main__.py
"""

import sys

import pytest

# Don't try to test if we're being imported
if __name__ == "__main__":
    sys.exit(pytest.main(["--pyargs", "potluck.tests"] + sys.argv[1:]))
