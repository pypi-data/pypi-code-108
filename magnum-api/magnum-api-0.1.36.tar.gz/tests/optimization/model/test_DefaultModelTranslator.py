import numpy as np

from magnumapi.cadata.CableDatabase import CableDatabase
from magnumapi.geometry.GeometryFactory import GeometryFactory
from magnumapi.optimization.design_variable import DesignVariableFactory
from magnumapi.optimization.design_variable.Individual import Individual
from magnumapi.optimization.model.ModelTranslator import DefaultModelTranslator
from tests.resource_files import create_resources_path

json_path = create_resources_path('resources/geometry/roxie/16T/16T_rel.json')
cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
cadata = CableDatabase.read_cadata(cadata_path)
geometry = GeometryFactory.init_with_json(json_path, cadata)


def test_generate_random_individual():
    np.random.seed(0)
    # arrange
    # initialize the design variables
    csv_global_file_path = create_resources_path('resources/optimization/optim_input_enlarged.csv')
    dv_gens = DesignVariableFactory.init_genetic_design_variables_with_csv(csv_global_file_path)
    # initialize an individual
    individual = Individual(gen_dvs=dv_gens)
    # initialize slotted geometry
    mt = DefaultModelTranslator(geometry)

    # act
    individual = mt.generate_random_individual(individual)

    # assert
    values = [dv.value for dv in individual.gen_dvs]
    values_ref = [5.953125, 9.78125, 4.75, 5.40625, 6.28125, 7.703125, 5.734375, 6.390625, 3.59375, 6.40625, 6.5625,
                  0.46875, 0.9375, 5.78125, 9.6875, 7.8125, 4, 3, 0, 0, 3, 10, 3, 13, 10, 1, 29, 10]
    assert values == values_ref


def test_update_geometry_parameters():
    np.random.seed(0)
    # arrange
    # initialize the design variables
    csv_global_file_path = create_resources_path('resources/optimization/optim_input_enlarged.csv')
    dv_gens = DesignVariableFactory.init_genetic_design_variables_with_csv(csv_global_file_path)
    # initialize an individual
    individual = Individual(gen_dvs=dv_gens)
    # initialize slotted geometry
    mt = DefaultModelTranslator(geometry)

    # act
    individual = mt.generate_random_individual(individual)
    block_layer_defs = mt.update_geometry(individual).to_dict()

    # assert
    block_defs_ref = {'block_defs': [
        {'alpha_r': 0, 'condname': '16TIL9', 'current': 13500, 'imag': 0, 'n1': 2, 'n2': 20, 'nco': 4, 'no': 1,
         'phi_r': 0.57294, 'radius': 25.0, 'turn': 0, 'type': 1},
        {'alpha_r': 3.59375, 'condname': '16TIL9', 'current': 13500, 'imag': 0, 'n1': 2, 'n2': 20, 'nco': 3, 'no': 2,
         'phi_r': 5.953125, 'radius': 25.0, 'turn': 0, 'type': 1},
        {'alpha_r': 0.0, 'condname': '16TIL9', 'current': 13500, 'imag': 0, 'n1': 2, 'n2': 20, 'nco': 3, 'no': 5,
         'phi_r': 0.36728, 'radius': 39.0, 'turn': 0, 'type': 1},
        {'alpha_r': 0.46875, 'condname': '16TIL9', 'current': 13500, 'imag': 0, 'n1': 2, 'n2': 20, 'nco': 10, 'no': 6,
         'phi_r': 5.40625, 'radius': 39.0, 'turn': 0, 'type': 1},
        {'alpha_r': 0.9375, 'condname': '16TIL9', 'current': 13500, 'imag': 0, 'n1': 2, 'n2': 20, 'nco': 3, 'no': 7,
         'phi_r': 6.28125, 'radius': 39.0, 'turn': 0, 'type': 1},
        {'alpha_r': 0, 'condname': '16TOL8', 'current': 13500, 'imag': 0, 'n1': 2, 'n2': 20, 'nco': 13, 'no': 8,
         'phi_r': 0.27026, 'radius': 53.0, 'turn': 0, 'type': 1},
        {'alpha_r': 5.78125, 'condname': '16TOL8', 'current': 13500, 'imag': 0, 'n1': 2, 'n2': 20, 'nco': 10, 'no': 9,
         'phi_r': 7.703125, 'radius': 53.0, 'turn': 0, 'type': 1},
        {'alpha_r': 9.6875, 'condname': '16TOL8', 'current': 13500, 'imag': 0, 'n1': 2, 'n2': 20, 'nco': 1, 'no': 10,
         'phi_r': 5.734375, 'radius': 53.0, 'turn': 0, 'type': 1},
        {'alpha_r': 0, 'condname': '16TOL8', 'current': 13500, 'imag': 0, 'n1': 2, 'n2': 20, 'nco': 29, 'no': 11,
         'phi_r': 0.21236, 'radius': 67.45, 'turn': 0, 'type': 1},
        {'alpha_r': 7.8125, 'condname': '16TOL8', 'current': 13500, 'imag': 0, 'n1': 2, 'n2': 20, 'nco': 10, 'no': 12,
         'phi_r': 6.390625, 'radius': 67.45, 'turn': 0, 'type': 1}],
        'layer_defs': [{'no': 1, 'symm': 1, 'typexy': 1, 'blocks': [1, 2]},
                       {'no': 2, 'symm': 1, 'typexy': 1, 'blocks': [5, 6, 7]},
                       {'no': 3, 'symm': 1, 'typexy': 1, 'blocks': [8, 9, 10]},
                       {'no': 4, 'symm': 1, 'typexy': 1, 'blocks': [11, 12]}]}

    assert block_defs_ref['block_defs'] == block_layer_defs['block_defs']
    assert block_defs_ref['layer_defs'] == block_layer_defs['layer_defs']
