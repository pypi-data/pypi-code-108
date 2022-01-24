import pytest

from magnumapi.optimization.config.ParallelOptimizationConfig import ParallelOptimizationConfig
from tests.resource_files import create_resources_path


json_path = create_resources_path('resources/optimization/parallel_config.json')
config = ParallelOptimizationConfig.initialize_config(json_path)


def test_initialize_config():
    # arrange
    # act
    # assert
    config_str = """root_abs_path: c:/gitlab/magnum-nb/
output_abs_path: c:/magnum/output/
optimization_folder: optimization_parallel
append_new_output_subdirectory: False
n_pop: 20
n_gen: 100
logger_rel_path: optimization_parallel/GeneticOptimization.csv
design_variables_rel_path: optimization/input/design_variables.csv

update_operator_config: 

type: elitism
params: {'n_elite': 2}
mutation_operator: OperatorConfig(type='default', params={'r_mut': 0.5})
selection_operator: OperatorConfig(type='default', params={'k_selection': 0.5})
crossover_operator: OperatorConfig(type='default', params={'r_cross': 0.5})

model_runner_config: 

geometry_input_rel_path: 16_rel_slotted_temp.json
geometry_type: slotted
cadata_input_rel_path: roxie2_old.cadata
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

notebook_folder: geometry_magnetic_for_parallel
notebook_name: Geometry_ROXIE.ipynb
input_parameters: {'index': 'index'}
output_parameters: ['b3', 'b5', 'bigb', 'margmi']
input_artefacts: {}
output_artefacts: []
ansys: 

ParallelAnsysConfig(run_dir='C:\\\\ansys', n_parallel_runners=10, n_proc=1, root_dir='mechanical_parallel', exec_file='', master_input_file='15T_mech_%d.inp', template_to_input_file={'15T_mech.template': '15T_mech_%d.inp', '15T_mech_post_roxie.template': '15T_mech_post_roxie_%d.inp', '15T_mech_solu.template': '15T_mech_solu_%d.inp', '15T_bc.template': '15T_bc_%d.inp', '15T_Coil_geo.template': '15T_Coil_geo_%d.inp', '15T_contact_el_m.template': '15T_contact_el_m_%d.inp', '15T_contact_mesh.template': '15T_contact_mesh_%d.inp', '15T_mat_and_elem.template': '15T_mat_and_elem_%d.inp', '15T_geometry_main.template': '15T_geometry_main_%d.inp', '15T_Yoke_geo.template': '15T_Yoke_geo_%d.inp', 'CoilBlockMacro_Roxie.mac': 'CoilBlockMacro_Roxie_%d.mac', 'ContactPropMacro.mac': 'ContactPropMacro_%d.mac'}, additional_upload_files=['Model_%d.inp', 'forces_edit_%d.vallone'])"""

    assert config_str == str(config)


def test_get_weight():
    # arrange
    objective = 'B_3_1'

    # act
    weight = config.get_weight(objective)

    # assert
    assert 0.1 == weight


def test_get_weight_error():
    # arrange
    objective = 'B_7_1'

    # act
    with pytest.raises(KeyError) as exc_info:
        config.get_weight(objective)

    # assert
    assert 'Objective name B_7_1 not present in objective configs.' in str(exc_info.value)


def test_get_constraint():
    # arrange
    objective = 'B_3_1'

    # act
    constraint = config.get_constraint(objective)

    # assert
    assert 0 == constraint


def test_get_constraint_error():
    # arrange
    objective = 'B_7_1'

    # act
    with pytest.raises(KeyError) as exc_info:
        config.get_constraint(objective)

    # assert
    assert 'Objective name B_7_1 not present in objective configs.' in str(exc_info.value)
