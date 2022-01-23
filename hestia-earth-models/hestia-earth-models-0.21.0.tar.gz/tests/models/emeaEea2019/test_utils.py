from unittest.mock import patch

from hestia_earth.models.emeaEea2019.utils import _get_fuel_values

class_path = 'hestia_earth.models.emeaEea2019.utils'
TERMS = [
    'diesel',
    'gasoline'
]


@patch(f"{class_path}._is_term_type_complete", return_value=True)
def test_get_fuel_values_no_inputs_complete(*args):
    cycle = {'inputs': []}
    assert _get_fuel_values(cycle) == ([0], [0])


@patch(f"{class_path}._is_term_type_complete", return_value=False)
def test_get_fuel_values_no_inputs_incomplete(*args):
    cycle = {'inputs': []}
    assert _get_fuel_values(cycle) == ([], [])


@patch(f"{class_path}.get_liquid_fuel_terms", return_value=TERMS)
def test_get_fuel_values(*args):
    cycle = {'inputs': [
        {
            'term': {'@id': 'diesel'},
            'value': [100]
        },
        {
            'term': {'@id': 'gasoline'},
            'value': [50]
        }
    ]}
    assert _get_fuel_values(cycle) == ([100], [50])
