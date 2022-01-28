"""Parse function tests."""

import pytest
from finesse.script import parse, parse_file
from .....util import dedent_multiline
from ....diff import assert_models_equivalent


@pytest.fixture
def model_kat_script():
    """Some uneventful kat model."""
    return dedent_multiline(
        """
        laser l0 P=1
        space s1 l0.p1 itm.p1
        mirror itm R=0.99 T=0.01
        space scav itm.p2 etm.p1 L=1
        mirror etm R=&itm.R T=&itm.T phi=&itm.phi
        pd pdcav itm.p1.o
        """
    )


@pytest.fixture
def model_via_string(model_kat_script):
    return parse(model_kat_script)


@pytest.fixture
def model_via_file(tmp_path, model_kat_script):
    """Test that parsing a string with kat script is the same as via a file."""
    tmpfile = tmp_path / "script.kat"
    with tmpfile.open(mode="w") as fp:
        fp.write(model_kat_script)
    with tmpfile.open(mode="r") as fp:
        return parse_file(fp)


def test_parse_function_is_same_as_model_parse_method(
    model_via_string, model, model_kat_script
):
    """Test that parsing directly with :meth:`.parse` results in the same model as
    :meth:`.Model.parse`."""
    model.parse(model_kat_script)
    assert_models_equivalent(model_via_string, model)


def test_parse_is_same_as_parse_file(tmp_path, model_via_string, model_via_file):
    """Test that parsing a string with kat script is the same as via a file."""
    assert_models_equivalent(model_via_string, model_via_file)
