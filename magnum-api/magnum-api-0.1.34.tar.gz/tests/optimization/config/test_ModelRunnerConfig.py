import pytest

from magnumapi.commons import json_file
from magnumapi.optimization.config.ModelRunnerConfig import ModelRunnerConfig
from tests.resource_files import create_resources_path

# arrange
model_runner_config_path = create_resources_path('resources/optimization/config/model_runner_config.json')
model_runner_config_dct = json_file.read(model_runner_config_path)

# act
model_runner_config = ModelRunnerConfig.initialize_config(model_runner_config_dct)


def test_initialize_config():
    # assert
    model_runner_config_str_ref = """geometry_input_rel_path: 
geometry_type: slotted
cadata_input_rel_path: 
is_notebook_scripted: True
model_creation_type: programmable

objectives: 

objective: B_3_1
weight: 0.100000
constraint: 0.000000

objective: B_5_1
weight: 0.100000
constraint: 0.000000

objective: MARGMI_0_0
weight: 1.000000
constraint: 0.850000

objective: seqv
weight: 0.001000
constraint: 0.000000

notebooks: 

notebook_folder: geometry
notebook_name: Geometry.ipynb
input_parameters: {}
output_parameters: []
input_artefacts: {}
output_artefacts: []

notebook_folder: magnetic
notebook_name: ROXIE.ipynb
input_parameters: {}
output_parameters: ['B_3_1', 'B_5_1', 'BIGB_1_1', 'MARGMI_0_0']
input_artefacts: {}
output_artefacts: ['magnetic/input/roxie_scaled.force2d']

notebook_folder: mechanical
notebook_name: ANSYS.ipynb
input_parameters: {}
output_parameters: ['seqv', 'sxmn', 'syin', 'symn', 'syou']
input_artefacts: {'input/roxie_scaled.force2d': 'magnetic/input/roxie_scaled.force2d'}
output_artefacts: []

notebook_folder: thermal
notebook_name: MIITs.ipynb
input_parameters: {'peak_field': 'BIGB_1_1'}
output_parameters: ['T_hotspot']
input_artefacts: {}
output_artefacts: []"""
    assert model_runner_config_str_ref == str(model_runner_config)


def test_get_weight():
    # arrange
    objective = 'B_3_1'

    # act
    weight = model_runner_config.get_weight(objective)

    # assert
    assert 0.1 == weight


def test_get_weight_error():
    # arrange
    objective = 'b7'

    # act
    with pytest.raises(KeyError) as context:
        model_runner_config.get_weight(objective)

    # assert
    assert 'Objective name b7 not present in objective configs.' in str(context.value)


def test_get_constraint():
    # arrange
    objective = 'B_3_1'

    # act
    constraint = model_runner_config.get_constraint(objective)

    # assert
    assert 0 == constraint


def test_get_constraint_error():
    # arrange
    objective = 'b7'

    # act
    with pytest.raises(KeyError) as context:
        model_runner_config.get_constraint(objective)

    # assert
    assert 'Objective name b7 not present in objective configs.' in str(context.value)
