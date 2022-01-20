from __future__ import annotations

import collections
import string

import importlib_resources
import pytest
import yaml

definition_yamls = collections.OrderedDict(
    (fn.name, fn)
    for fn in importlib_resources.files("dials_data").joinpath("definitions").iterdir()
    if fn.suffix != ".MD"
)
hashinfo_yamls = collections.OrderedDict(
    (fn.name, fn)
    for fn in importlib_resources.files("dials_data").joinpath("hashinfo").iterdir()
    if fn.suffix != ".MD"
)


def is_valid_name(fileobj):
    if fileobj.suffix != ".yml" or len(fileobj.stem) <= 1:
        return False
    allowed_characters = frozenset(string.ascii_letters + string.digits + "_")
    return all(c in allowed_characters for c in fileobj.stem)


@pytest.mark.parametrize(
    "yaml_file", list(definition_yamls.values()), ids=list(definition_yamls.keys())
)
def test_yaml_file_is_valid_definition(yaml_file):
    assert is_valid_name(yaml_file)
    definition = yaml.safe_load(yaml_file.read_bytes())
    fields = set(definition)
    required = {"name", "data", "description"}
    optional = {"license", "url", "author"}
    assert fields >= required, "Required fields missing: " + str(
        sorted(required - fields)
    )
    assert fields <= (required | optional), "Unknown fields present: " + str(
        sorted(fields - required - optional)
    )
    assert definition["data"], "Data definition is empty"
    for n, entry in enumerate(definition["data"]):
        assert isinstance(
            entry, dict
        ), f"Data definition #{n+1} contains non-dictionary entry: {entry!r}"
        assert "url" in entry, f"Data definition #{n+1} does not specify a URL"


@pytest.mark.parametrize(
    "yaml_file", list(hashinfo_yamls.values()), ids=list(hashinfo_yamls.keys())
)
def test_yaml_file_is_valid_hashinfo(yaml_file):
    assert is_valid_name(yaml_file)
    assert (
        yaml_file.name in definition_yamls
    ), "hashinfo file present without corresponding definition file"
    hashinfo = yaml.safe_load(yaml_file.read_bytes())
    fields = set(hashinfo)
    required = {"definition", "formatversion", "verify"}
    assert fields >= required, "Required fields missing: " + str(
        sorted(required - fields)
    )
    assert fields <= required, "Unknown fields present: " + str(
        sorted(fields - required)
    )
