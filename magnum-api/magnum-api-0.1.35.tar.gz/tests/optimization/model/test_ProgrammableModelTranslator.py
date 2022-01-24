import numpy as np
import pandas as pd

from magnumapi.cadata.CableDatabase import CableDatabase
from magnumapi.geometry.GeometryFactory import GeometryFactory
from magnumapi.optimization.design_variable import DesignVariableFactory
from magnumapi.optimization.design_variable.Individual import Individual
from magnumapi.optimization.model.ModelTranslator import ProgrammableModelTranslator
from tests.resource_files import create_resources_path

json_path = create_resources_path('resources/geometry/roxie/16T/16T_rel_slotted.json')
cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
cadata = CableDatabase.read_cadata(cadata_path)
geometry = GeometryFactory.init_slotted_with_json(json_path, cadata)
csv_global_file_path = create_resources_path(
    'resources/optimization/mock_programmable/design_variables_programmable_geometry.csv')
dv_gens = DesignVariableFactory.init_genetic_design_variables_with_csv(csv_global_file_path)


def test_generate_random_individual():
    np.random.seed(0)
    # arrange
    # initialize an individual
    individual = Individual(gen_dvs=dv_gens)
    # initialize slotted geometry
    mt = ProgrammableModelTranslator(geometry)

    # act
    individual = mt.generate_random_individual(individual)

    # assert
    values = [dv.value for dv in individual.gen_dvs]
    values_ref = [1.9375, 16, 4, 10, 4, 2, 0, 0, 0, 1.15625, 1.96875, 1.9375, 2.5625, 1.1875, -1.40625, 0.3125, 4.0625,
                  -1.5625, -1.71875, 2.34375, 23, 4, 18, 4, 1, 0, 0, 1.625, 1.65625, 1.03125, 1.25, 2.15625, 1.375,
                  1.75, 1.3125, 2.53125, 33, 4, 12, 9, 9, 3, 0, 1.4375, 1.9375, 1.40625, 1.34375, 2.53125, 2.71875,
                  2.1875, 1.40625, 1.59375, 41, 1, 41, 0, 0, 2.875, 1.65625, 2.0625, 1.9375]
    assert values == values_ref


def test_split_list_into_chunks():
    # To produce a partition of t into k values:
    #
    # - Generate k-1 uniformly distributed values in the range [0, t].
    #
    # - Sort them, and add 0 at the beginning and t at the end.
    #
    # - Use the adjacent differences as the partition.
    np.random.seed(0)
    t = 30
    k = 4
    partition = ProgrammableModelTranslator._generate_number_random_partition(t, k)

    assert [13, 8, 6, 3] == partition


def test_update_geometry_parameters():
    np.random.seed(10)
    # arrange
    # initialize an individual
    individual = Individual(gen_dvs=dv_gens)
    # initialize slotted geometry
    mt = ProgrammableModelTranslator(geometry)

    # act
    individual = mt.generate_random_individual(individual)
    block_layer_defs = mt.update_geometry(individual).to_dict()

    # assert
    block_defs_ref = {'r_aperture': 25.0, 'block_defs': [
        {'no': 1, 'type': 1, 'nco': 5, 'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0,
         'radius': 27.5625, 'phi_r': 1.03943623529265, 'alpha_r': -2.382415281582425e-16},
        {'no': 2, 'type': 1, 'nco': 3, 'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0,
         'radius': 27.5625, 'phi_r': 0.5162584403839361, 'alpha_r': 27.875121680200177},
        {'no': 3, 'type': 1, 'nco': 3, 'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0,
         'radius': 27.5625, 'phi_r': 4.367815516681844, 'alpha_r': 15.460212071537764},
        {'no': 4, 'type': 1, 'nco': 2, 'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0,
         'radius': 27.5625, 'phi_r': 8.15750494673803, 'alpha_r': 17.078760809821418},
        {'no': 5, 'type': 1, 'nco': 12, 'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0,
         'radius': 42.6, 'phi_r': 0.6725011161819067, 'alpha_r': -2.3824152815824267e-16},
        {'no': 6, 'type': 1, 'nco': 4, 'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0,
         'radius': 42.6, 'phi_r': 5.250000000000007, 'alpha_r': 36.07542667742755},
        {'no': 7, 'type': 1, 'nco': 13, 'current': 13500, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0,
         'radius': 58.356249999999996, 'phi_r': 0.4909198292067958, 'alpha_r': -2.30472783679382e-16},
        {'no': 8, 'type': 1, 'nco': 9, 'current': 13500, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0,
         'radius': 58.356249999999996, 'phi_r': 4.5937500000000036, 'alpha_r': 17.392731530748346},
        {'no': 9, 'type': 1, 'nco': 5, 'current': 13500, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0,
         'radius': 58.356249999999996, 'phi_r': 5.859137095545925, 'alpha_r': 9.256232255161258},
        {'no': 10, 'type': 1, 'nco': 2, 'current': 13500, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0,
         'radius': 58.356249999999996, 'phi_r': 5.800320588188178, 'alpha_r': 6.2026565791092025},
        {'no': 11, 'type': 1, 'nco': 35, 'current': 13500, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0,
         'turn': 0, 'radius': 73.9375, 'phi_r': 0.38746384595595507, 'alpha_r': -2.304727836793822e-16}],
                      'layer_defs': [{'no': 1, 'symm': 1, 'typexy': 1, 'blocks': [1, 2, 3, 4], 'spar_thickness': 2.5625,
                                      'midplane_wedge_thickness': 0.5},
                                     {'no': 2, 'symm': 1, 'typexy': 1, 'blocks': [5, 6], 'spar_thickness': 1.6875,
                                      'midplane_wedge_thickness': 0.5},
                                     {'no': 3, 'symm': 1, 'typexy': 1, 'blocks': [7, 8, 9, 10],
                                      'spar_thickness': 2.40625, 'midplane_wedge_thickness': 0.5},
                                     {'no': 4, 'symm': 1, 'typexy': 1, 'blocks': [11], 'spar_thickness': 1.78125,
                                      'midplane_wedge_thickness': 0.5}]}
    pd.testing.assert_frame_equal(pd.DataFrame(block_defs_ref['block_defs']),
                                  pd.DataFrame(block_layer_defs['block_defs']))
    pd.testing.assert_frame_equal(pd.DataFrame(block_defs_ref['layer_defs']),
                                  pd.DataFrame(block_layer_defs['layer_defs']))
