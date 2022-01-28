import pytest
from finesse.script import parse, unparse


@pytest.fixture
def unparsed_script():
    def getmodel(user_gouy=""):
        return unparse(
            parse(
                f"""
            l l1
            s s0 l1.p1 m1.p1 {user_gouy}
            m m1
            """
            )
        )

    return getmodel


def test_no_user_gouy(unparsed_script):
    assert "user_gouy" not in unparsed_script()
    assert "user_gouy" not in unparsed_script("user_gouy_x=None user_gouy_y=None")


def test_with_user_gouy(unparsed_script):
    assert "user_gouy_x=1" in unparsed_script("user_gouy_x=1")
    assert "user_gouy_x=1" in unparsed_script("user_gouy_x=1 user_gouy_y=1")

    assert "user_gouy_y=1" in unparsed_script("user_gouy_y=1")
    assert "user_gouy_y=1" in unparsed_script("user_gouy_x=1 user_gouy_y=1")
