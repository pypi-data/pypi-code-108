from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.ipcc2019.ch4ToAirEntericFermentation import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}._get_DE_type", return_value='')
@patch(f"{class_path}._get_liveAnimal_lookup_value", return_value=0)
@patch(f"{class_path}.get_feed", return_value=0)
def test_should_run(mock_feed, mock_lookup_value, *args):
    cycle = {
        "inputs": [
            {
                "term": {
                    "@type": "Term",
                    "termType": "crop",
                    "@id": "sugarcaneMolasses",
                    "units": "kg",
                },
                "value": [0.000618],
            }
        ]
    }
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with fermentation factor => no run
    mock_lookup_value.return_value = 2
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with feed  => run
    mock_feed.return_value = 2
    should_run, *args = _should_run(cycle)
    assert should_run is True


# patch get_node_property to read value from lookups only
@patch('hestia_earth.models.utils.crop.get_node_property', return_value=None)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


# patch get_node_property to read value from lookups only
@patch('hestia_earth.models.utils.crop.get_node_property', return_value=None)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_dairy(*args):
    with open(f"{fixtures_folder}/dairy-buffalo-cows/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/dairy-buffalo-cows/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


# patch get_node_property to read value from lookups only
@patch('hestia_earth.models.utils.crop.get_node_property', return_value=None)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_non_dairy(*args):
    with open(f"{fixtures_folder}/non-dairy-buffalo-cows/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/non-dairy-buffalo-cows/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


# patch get_node_property to read value from lookups only
@patch('hestia_earth.models.utils.crop.get_node_property', return_value=None)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_with_ionophores(*args):
    with open(f"{fixtures_folder}/with-ionophores/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-ionophores/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


# patch get_node_property to read value from lookups only
@patch('hestia_earth.models.utils.crop.get_node_property', return_value=None)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_without_ionophores(*args):
    with open(f"{fixtures_folder}/without-ionophores/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/without-ionophores/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


# patch get_node_property to read value from lookups only
@patch('hestia_earth.models.utils.crop.get_node_property', return_value=None)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_no_feed(*args):
    with open(f"{fixtures_folder}/no-feed/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    result = run(cycle)
    assert result == []
