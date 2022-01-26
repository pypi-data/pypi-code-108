from pathlib import Path

import ckan.plugins.toolkit as tk
import pytest

from ckanext.iso19115 import utils


@pytest.fixture(scope="session")
def examples():
    return Path(__file__).parent / "examples"


@pytest.fixture()
def example(examples, request):
    name = next(
        m.args[0]
        for m in request.node.iter_markers()
        if m.name == "xml_example"
    )
    path = examples / name
    return path.open("rb").read()


@pytest.fixture()
def schema_errors(example):
    try:
        utils.validate_schema(example, validate_codelists=True)
    except tk.ValidationError as e:
        return e.error_dict["schema"]
    return []


@pytest.fixture()
def schematron_errors(example, request):
    schemas = {
        m.name[len("schematron_") :]
        for m in request.node.iter_markers()
        if m.name.startswith("schematron_")
    }
    try:
        utils.validate_schematron(example, schemas)
    except tk.ValidationError as e:
        return e.error_dict["schematron"]
    return []
