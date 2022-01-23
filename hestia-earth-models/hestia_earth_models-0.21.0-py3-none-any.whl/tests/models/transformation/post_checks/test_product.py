import json

from hestia_earth.schema import TermTermType
from tests.utils import fixtures_path

from hestia_earth.models.transformation.post_checks.product import run, _should_run

fixtures_folder = f"{fixtures_path}/transformation/post_checks/product"


def test_should_run():
    transformation = {'term': {}}

    # not an excreta management => no run
    transformation['term']['termType'] = TermTermType.ANIMALMANAGEMENT.value
    assert not _should_run(transformation)

    # is an excreta management => no run
    transformation['term']['termType'] = TermTermType.EXCRETAMANAGEMENT.value
    assert _should_run(transformation) is True


def test_run():
    with open(f"{fixtures_folder}/transformation.jsonld", encoding='utf-8') as f:
        transformation = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(transformation)
    assert value == expected


def test_run_with_input_nitrogen():
    with open(f"{fixtures_folder}/with-input-nitrogen/transformation.jsonld", encoding='utf-8') as f:
        transformation = json.load(f)

    with open(f"{fixtures_folder}/with-input-nitrogen/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(transformation)
    assert value == expected
