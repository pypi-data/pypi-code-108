import numpy as np
import pandas as pd

from magnumapi.cadata.CableDatabase import CableDatabase
from magnumapi.geometry.GeometryChange import GeometryChange
from magnumapi.geometry.GeometryFactory import GeometryFactory
from magnumapi.optimization.design_variable import DesignVariableFactory
from magnumapi.optimization.design_variable.GeneticDesignVariable import GeneticBlockDesignVariable
from magnumapi.optimization.design_variable.Individual import Individual
from magnumapi.optimization.model.ModelTranslator import TargetedModelTranslator
from tests.resource_files import create_resources_path

json_path = create_resources_path('resources/geometry/roxie/16T/16T_rel.json')
cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
cadata = CableDatabase.read_cadata(cadata_path)
geometry = GeometryFactory.init_with_json(json_path, cadata)


def test_generate_random_individual():
    np.random.seed(0)
    # arrange
    # initialize the design variables
    csv_global_file_path = create_resources_path(
        'resources/optimization/mock_targeted/design_variables_targeted_geometry.csv')
    dv_gens = DesignVariableFactory.init_genetic_design_variables_with_csv(csv_global_file_path)
    # initialize an individual
    individual = Individual(gen_dvs=dv_gens)
    # initialize slotted geometry
    mt = TargetedModelTranslator(geometry)

    # act
    individual = mt.generate_random_individual(individual)

    # assert
    values = [dv.value for dv in individual.gen_dvs]
    values_ref = [3.84375, 4.9375, 3.5, 3.6875, 3.9375, 4.34375, 3.78125, 3.96875, -0.703125, 0.703125, 0.78125,
                  -2.265625, -2.03125, 0.390625, 2.34375, 1.40625, 2, 2, 2, 2, 2, 2, -2, -1]
    assert values == values_ref


def test_correct_missing_blocks_in_block_and_layer_definitions():
    # arrange
    dv1 = GeneticBlockDesignVariable(xl=0, xu=2, variable_type='int', variable='nco_r', layer=1, bcs=1, bits=3)
    dv1.gene = dv1.convert_int_to_gene(2, dv1.bits)
    dv2 = GeneticBlockDesignVariable(xl=-3, xu=2, variable_type='int', variable='nco_r', layer=1, bcs=2, bits=3)
    dv2.gene = dv2.convert_int_to_gene(0, dv2.bits)
    individual = Individual([dv1, dv2])

    json_path = create_resources_path('resources/geometry/roxie/16T/16T_rel.json')
    cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
    cadata = CableDatabase.read_cadata(cadata_path)
    geometry = GeometryFactory.init_with_json(json_path, cadata)

    # act
    # # update number of turns per block_index
    geometry = GeometryChange.update_nco_r(geometry, individual)

    assert len(geometry.blocks) == 11
    assert geometry.layer_defs[0].blocks == [1, 3, 4]
    assert geometry.layer_defs[1].blocks == [5, 6, 7]
    assert geometry.layer_defs[2].blocks == [8, 9, 10]
    assert geometry.layer_defs[3].blocks == [11, 12]


def test_update_geometry_parameters():
    np.random.seed(0)
    # arrange
    # initialize the design variables
    csv_global_file_path = create_resources_path(
        'resources/optimization/mock_targeted/design_variables_targeted_geometry.csv')
    dv_gens = DesignVariableFactory.init_genetic_design_variables_with_csv(csv_global_file_path)
    # initialize an individual
    individual = Individual(gen_dvs=dv_gens)
    # initialize slotted geometry
    mt = TargetedModelTranslator(geometry)

    # act
    individual = mt.generate_random_individual(individual)
    block_layer_defs = mt.update_geometry(individual).to_dict()

    # assert
    block_defs_ref = {'block_defs': [
        {'no': 1, 'type': 1, 'nco': 6, 'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0,
         'radius': 25.0, 'phi_r': 0.5729399999999999, 'alpha_r': -1.1912076407912136e-16},
        {'no': 2, 'type': 1, 'nco': 5, 'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0,
         'radius': 25.0, 'phi_r': 3.140625, 'alpha_r': 40.942397820646725},
        {'no': 3, 'type': 1, 'nco': 2, 'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0,
         'radius': 25.0, 'phi_r': 6.783197903156847, 'alpha_r': 20.828315994424038},
        {'no': 5, 'type': 1, 'nco': 9, 'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0,
         'radius': 39.0, 'phi_r': 0.36728, 'alpha_r': -1.1912076407912134e-16},
        {'no': 6, 'type': 1, 'nco': 10, 'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0,
         'radius': 39.0, 'phi_r': 1.4218749999999964, 'alpha_r': 40.020395810666486},
        {'no': 8, 'type': 1, 'nco': 20, 'current': 13500, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0,
         'radius': 53.0, 'phi_r': 0.27026000000000006, 'alpha_r': -1.152363918396911e-16},
        {'no': 9, 'type': 1, 'nco': 5, 'current': 13500, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0,
         'radius': 53.0, 'phi_r': 4.734375000000007, 'alpha_r': 26.874263974299037},
        {'no': 10, 'type': 1, 'nco': 4, 'current': 13500, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0,
         'radius': 53.0, 'phi_r': 6.1612573300830675, 'alpha_r': 8.153015330118137},
        {'no': 11, 'type': 1, 'nco': 27, 'current': 13500, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0,
         'turn': 0, 'radius': 67.45, 'phi_r': 0.21236000000000002, 'alpha_r': -1.152363918396911e-16},
        {'no': 12, 'type': 1, 'nco': 12, 'current': 13500, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0,
         'turn': 0, 'radius': 67.45, 'phi_r': 6.331916480253511, 'alpha_r': 27.098221287180614}],
        'layer_defs': [{'no': 1, 'symm': 1, 'typexy': 1, 'blocks': [1, 2, 3]},
                       {'no': 2, 'symm': 1, 'typexy': 1, 'blocks': [5, 6]},
                       {'no': 3, 'symm': 1, 'typexy': 1, 'blocks': [8, 9, 10]},
                       {'no': 4, 'symm': 1, 'typexy': 1, 'blocks': [11, 12]}]}

    pd.testing.assert_frame_equal(pd.DataFrame(block_defs_ref['block_defs']),
                                  pd.DataFrame(block_layer_defs['block_defs']))
    pd.testing.assert_frame_equal(pd.DataFrame(block_defs_ref['layer_defs']),
                                  pd.DataFrame(block_layer_defs['layer_defs']))


def test_update_model_parameters_targeted():
    np.random.seed(1)

    # act
    path_str = 'resources/optimization/mock_targeted/design_variables_targeted_geometry.csv'
    csv_global_file_path = create_resources_path(path_str)
    dv_gens = DesignVariableFactory.init_genetic_design_variables_with_csv(csv_global_file_path)

    # initialize an individual
    individual = Individual(gen_dvs=dv_gens)

    # initialize slotted geometry
    mt = TargetedModelTranslator(geometry)
    individual = mt.generate_random_individual(individual)
    geometry_rel = mt.update_geometry(individual)

    # assert that the number of turns per layer is the same
    assert 13 == sum([block.block_def.nco for block in geometry_rel.blocks[:4]])
    assert 19 == sum([block.block_def.nco for block in geometry_rel.blocks[4:7]])
    assert 29 == sum([block.block_def.nco for block in geometry_rel.blocks[7:10]])
    assert 39 == sum([block.block_def.nco for block in geometry_rel.blocks[10:]])
