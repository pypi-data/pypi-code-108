import os
import unittest
import gammalearn.utils as utils
import numpy as np
from ctapipe.instrument import CameraGeometry
from copy import deepcopy
import astropy.units as u


class MockLSTDataset(object):

    def __init__(self):

        self.images = np.array([np.full(1855, 0.001),
                                np.full(1855, 1),
                                np.full(1855, 0.0001),
                                np.full(1855, 0.1)])
        self.images[3, 903:910] = 30
        self.images[2, 1799:1806] = 10  # for cleaning and leakage
        self.camera_type = 'LST_LSTCam'
        self.group_by = 'image'
        self.original_geometry = CameraGeometry.from_name('LSTCam')
        self.simu = True
        self.dl1_params = {
            'event_id': np.array([0, 0, 1, 2]),
            'mc_type': np.array([1, 0, 0, 0]),
            'mc_energy': np.array([0.010, 2.5, 0.12, 0.8]),
            'log_mc_energy': np.log10(np.array([0.010, 2.5, 0.12, 0.8])),
            'mc_alt_tel': np.full(4, np.deg2rad(70)),
            'mc_az_tel': np.full(4, np.deg2rad(180)),
            'mc_alt': np.deg2rad([71, 75, 68, 69]),
            'mc_az': np.deg2rad([180, 180, 179.5, 175]),
            'mc_core_x': np.array([50.3, -150, -100, 100])/1000,
            'mc_core_y': np.array([48, -51, 0, 0])/1000,
            'tel_id': np.array([2, 1, 3, 1]),
            'tel_pos_x': np.array([75.28, -70.93, -70.93, -70.93])/1000,
            'tel_pos_y': np.array([50.46, -52.07, 53.1, -52.07])/1000,
        }

    def __len__(self):
        return len(self.images)


class TestUtils(unittest.TestCase):

    def setUp(self) -> None:

        self.intensity_filter_parameters = [300, np.inf]
        self.intensity_true_mask = [False, True, False, True]

        self.cleaning_filter_parameters = {'picture_thresh': 6, 'boundary_thresh': 3,
                                           'keep_isolated_pixels': False, 'min_number_picture_neighbors': 2}
        self.cleaning_true_mask = [False, False, True, True]

        self.leakage_parameters = {'leakage2_cut': 0.2, 'picture_thresh': 6, 'boundary_thresh': 3,
                                   'keep_isolated_pixels': False, 'min_number_picture_neighbors': 2}
        self.leakage_true_mask = [False, False, False, True]

        self.energy_parameters = {'energy': [0.02, 2], 'filter_only_gammas': True}
        self.energy_true_mask = [True, False, True, True]

        self.emission_cone_parameters = {'max_angle': np.deg2rad(4.)}
        self.emission_cone_true_mask = [True, False, True, True]

        self.impact_distance_parameters = {'max_distance': 0.05}
        self.impact_distance_true_mask = [True, False, False, False]

        self.multiplicity_parameters = {'multiplicity': 2}
        self.multiplicity_true_mask = [True, True, False, False]
        self.multiplicity_strict_parameters = {'multiplicity': 1, 'strict': True}
        self.multiplicity_strict_true_mask = [False, False, True, True]
        self.multiplicity_strict_true_trig_energies = np.array([0.010, 0.12, 0.8])

    def test_emission_cone(self):
        self.dataset = MockLSTDataset()
        assert np.all(utils.emission_cone_filter(self.dataset, **self.emission_cone_parameters) ==
                      self.emission_cone_true_mask)

    def test_impact_distance(self):
        self.dataset = MockLSTDataset()
        assert np.all(utils.impact_distance_filter(self.dataset, **self.impact_distance_parameters) ==
                      self.impact_distance_true_mask)

    def test_multiplicity(self):
        self.dataset = MockLSTDataset()
        assert np.all(utils.telescope_multiplicity_filter(self.dataset, **self.multiplicity_parameters) ==
                      self.multiplicity_true_mask)

    def test_multiplicity_strict(self):
        self.dataset = MockLSTDataset()
        assert np.all(utils.telescope_multiplicity_filter(self.dataset, **self.multiplicity_strict_parameters) ==
                      self.multiplicity_strict_true_mask)

    def test_energy(self):
        self.dataset_lst = MockLSTDataset()
        assert np.all(utils.energyband_filter(self.dataset_lst, **self.energy_parameters) ==
                      self.energy_true_mask)

    def test_leakage(self):
        self.dataset = MockLSTDataset()
        assert np.all(utils.leakage_filter(self.dataset, **self.leakage_parameters) ==
                      self.leakage_true_mask)

    def test_cleaning(self):
        self.dataset = MockLSTDataset()
        assert np.all(utils.cleaning_filter(self.dataset, **self.cleaning_filter_parameters) ==
                      self.cleaning_true_mask)

    def test_rotated_indices(self):
        pix_pos = np.transpose([[0, 1, 0, -1], [1, 0, -1, 0]])

        np.testing.assert_array_equal(utils.rotated_indices(pix_pos, 0), [0, 1, 2, 3])
        np.testing.assert_array_equal(utils.rotated_indices(pix_pos, np.pi/2), [1, 2, 3, 0])
        np.testing.assert_array_equal(utils.rotated_indices(pix_pos, -np.pi / 2), [3, 0, 1, 2])

    def test_nets_definition_path(self):
        path = utils.nets_definition_path()
        assert os.path.exists(path)


class TestIndexMatrix(unittest.TestCase):

    def setUp(self):
        lstcam_geom = CameraGeometry.from_name('LSTCam-002')
        self.minihex = deepcopy(lstcam_geom)
        self.minihex.camera_name = 'minihex'

    def test_get_index_matrix_from_geom_7(self):
        """
        Test the converter with a simple 7 pixels geometry

        Hexa:
        ```
          0   1

        2   3   4

          5   6
        ```
        Square:
        ```
         0   1  -1
         2   3   4
        -1   5   6
        ```
        """
        minihex = self.minihex
        # make a test geometry with 7 pixels
        minihex.n_pixels = 7
        short_dist = np.sqrt(3) / 2
        minihex.pix_x = 0.05 * np.array([-0.5, 0.5, -1, 0, 1, -0.5, 0.5]) * u.m
        minihex.pix_y = 0.05 * np.array([short_dist, short_dist, 0, 0, 0, -short_dist, -short_dist]) * u.m
        minihex.pix_rotation *= 0
        minihex.neighbors = minihex.neighbors[:7]
        minihex.pix_id = minihex.pix_id[:7]
        minihex.pixel_width = minihex.pixel_width[:7]

        # fix the neighbors
        minihex.neighbors = [
            [1, 2, 3],
            [0, 3, 4],
            [0, 3, 5],
            [0, 1, 2, 4, 5, 6],
            [1, 3, 6],
            [2, 3, 6],
            [4, 3, 5]
        ]

        idx_mat = utils.get_index_matrix_from_geom(minihex)

        np.testing.assert_array_equal(idx_mat, [[ 0,  1, -1],
                                                [ 2,  3,  4],
                                                [-1,  5,  6]])

    def test_get_index_matrix_from_geom_19(self):
        """
        Test the converter with a simple 19 pixels geometry

        Hexa:
        ```

             0   1   2

           3   4   5   6

          7  8   9  10  11

            12 13  14  15

              16 17 18
        ```
        Square:
        ```
         0   1   2  -1  -1

         3   4   5   6  -1

         7   8   9  10  11

        -1  12  13  14  15

        -1  -1  16  17  18
        ```
        """
        minihex = self.minihex

        minihex.n_pixels = 19
        short_dist = np.sqrt(3) / 2
        minihex.pix_x = 0.05 * np.array([-1, 0, 1,
                                         -1.5, -0.5, 0.5, 1.5,
                                         -2, -1, 0, 1, 2,
                                         -1.5, -0.5, 0.5, 1.5,
                                         -1, 0, 1,
                                         ]) * u.m

        minihex.pix_y = 0.05 * np.array([2 * short_dist, 2 * short_dist, 2 * short_dist,
                                         short_dist, short_dist, short_dist, short_dist,
                                         0, 0, 0, 0, 0,
                                         -short_dist, -short_dist, -short_dist, -short_dist,
                                         -2 * short_dist, -2 * short_dist, -2 * short_dist,
                                         ]) * u.m

        minihex.pix_rotation *= 0

        minihex.neighbors = minihex.neighbors[:minihex.n_pixels]
        minihex.pix_id = minihex.pix_id[:minihex.n_pixels]
        minihex.pixel_width = minihex.pixel_width[:minihex.n_pixels]

        # fix the neighbors
        minihex.neighbors = [
            [1, 3, 4],
            [0, 4, 5, 2],
            [1, 5, 6],
            [0, 4, 7, 8],
            [0, 1, 5, 9, 8, 3],
            [1, 2, 6, 10, 9, 4],
            [2, 5, 10, 11],
            [7, 8, 12],
            [3, 4, 9, 13, 12, 7],
            [4, 5, 10, 14, 13, 8],
            [5, 6, 11, 15, 14, 9],
            [6, 10, 15],
            [7, 8, 13, 16],
            [8, 9, 14, 17, 16, 12],
            [9, 10, 15, 18, 17, 13],
            [10, 11, 14, 18],
            [12, 13, 17],
            [13, 14, 16, 18],
            [14, 15, 17],
        ]

        idx_mat = utils.get_index_matrix_from_geom(minihex)

        np.testing.assert_array_equal(idx_mat, [[ 0,  1,  2, -1, -1],
                                                [ 3,  4,  5,  6, -1],
                                                [ 7,  8,  9, 10, 11],
                                                [-1, 12, 13, 14, 15],
                                                [-1, -1, 16, 17, 18]])


    def test_compare_indexedconv_method(self):
        """
        Test that the new method gives the same result as the previous one for the LSTCam geometry
        """
        import indexedconv.utils as cvutils
        from gammalearn.utils import load_camera_parameters

        lst_params = load_camera_parameters('LST_LSTCam')
        idx_mat = cvutils.create_index_matrix(lst_params['nbRow'], lst_params['nbCol'], lst_params['injTable'])
        lst_geom = CameraGeometry.from_name('LSTCam')
        new_idx_mat, camera_layout = utils.get_camera_layout_from_geom(lst_geom)

        assert camera_layout == 'Hex'
        np.testing.assert_array_equal(idx_mat.numpy(), new_idx_mat.numpy())





if __name__ == '__main__':
    unittest.main()
