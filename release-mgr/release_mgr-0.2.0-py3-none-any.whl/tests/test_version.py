import pytest

from release_mgr.version import Version


@pytest.mark.parametrize(
    ("verstring", "expected"),
    [
        ("0.0.0", True),
        ("0.0.0-beta", True),
        ("0.1.0", True),
        ("1010.100.0", True),
        ("1010.100.0-suffix", True),
        ("mat", False),
    ],
)
def test_is_version_string(verstring, expected):
    assert Version.is_version_string(verstring) == expected


def test_sorted():
    expected = [
        Version(0, 1, 0),
        Version(0, 2, 0),
        Version(0, 2, 1),
        Version(0, 3, 0),
        Version(0, 3, 1, suffix="beta"),
        Version(0, 3, 1),
        Version(1, 0, 0),
    ]

    inputs = [
        "0.1.0",
        "0.3.1",
        "0.2.1",
        "0.3.1-beta",
        "0.2.0",
        "0.3.0",
        "1.0.0",
    ]

    versions = [Version.from_str(verstr) for verstr in inputs]

    assert list(sorted(versions)) == expected
