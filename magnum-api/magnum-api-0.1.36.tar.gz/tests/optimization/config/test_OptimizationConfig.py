
from magnumapi.optimization.config.OptimizationConfig import OptimizationConfig
from tests.resource_files import create_resources_path


json_path = create_resources_path('resources/optimization/config/genetic_optimization_config.json')
config = OptimizationConfig.initialize_config(json_path)


def test_initialize_config():
    # arrange
    # act
    # assert
    config_str_ref = """root_abs_path: c:/gitlab/magnum-nb/
output_abs_path: c:/magnum/output/
optimization_folder: optimization
append_new_output_subdirectory: False
n_pop: 20
n_gen: 100
logger_rel_path: optimization/GeneticOptimization.csv
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

    assert config_str_ref == str(config)
