import pytest

from magnumapi.optimization.design_variable.DesignVariable import DesignVariable, \
    LayerDesignVariable, BlockDesignVariable, MultiBlockDesignVariable

global_def = DesignVariable(variable='R_EE', xl=0, xu=10, variable_type='int')
layer_def = LayerDesignVariable(variable='current', xl=100.10, xu=130, variable_type='float', layer=1)
turn_def = BlockDesignVariable(variable='phi', xl=-3.5, xu=3.5, variable_type='float', layer=1, bcs=2)
multiturn_def = MultiBlockDesignVariable(variable='alpha', xl=-4.5, xu=4.5, variable_type='float',
                                         layer=1, bcs='1-13')


@pytest.mark.parametrize('definition,expected_output', zip([global_def, layer_def, turn_def, multiturn_def],
                                                           ['R_EE', 'current:1', 'phi:1:2', 'alpha:1:1-13']))
def test_get_compact_variable_name(definition, expected_output):
    assert definition.get_compact_variable_name() == expected_output


@pytest.mark.parametrize('definition,value,expected_output', zip([global_def, layer_def, turn_def, multiturn_def],
                                                                 [5, 123.1, 0, 1],
                                                                 [0.5, 0.769, 0.5, 0.611]))
def test_get_fraction(definition, value, expected_output):
    assert (definition.get_fraction(value) - expected_output) < 1e-3


@pytest.mark.parametrize('definition,value,expected_output', zip([global_def, layer_def, turn_def, multiturn_def],
                                                                 [5, 123.1, 0, 1],
                                                                 ['value: 5, range: [0, 10]',
                                                                  'value: 123.100, range: [100.100, 130.000]',
                                                                  'value: 0.000, range: [-3.500, 3.500]',
                                                                  'value: 1.000, range: [-4.500, 4.500]']))
def test_get_hover_text(definition, value, expected_output):
    assert definition.get_hover_text(value) == expected_output
