import unittest
import os
import collections
import numpy as np
import gammalearn.datasets as dsets
import gammalearn.utils as utils
from gammalearn.logging import LOGGING_CONFIG
import logging

import warnings
warnings.filterwarnings("ignore")

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

logging.config.dictConfig(LOGGING_CONFIG)


class TestLSTDataset(unittest.TestCase):

    def setUp(self) -> None:
        self.data_file = os.path.join(THIS_DIR, '../../share/data/MC_data/dl1_gamma_example.h5')
        self.camera_type = 'LST_LSTCam'
        self.particle_dict = {0: 1, 1: 0, 101: 0}
        self.subarray = [1]
        self.targets = collections.OrderedDict({
            'energy': {
                'output_shape': 1,
            },
            'impact': {
                'output_shape': 2,
            },
            'direction': {
                'output_shape': 2,
            },
            'class': {
                'output_shape': 2,
                'label_shape': 1,
            },
        })
        self.group_by_image = {
            0: {
                'image_0': np.float32(1.5583277),
                'time_0': np.float32(-0.31744528),
                'labels': {
                    'energy': np.float32(0.3544642),
                    'corex': np.float32(-158.21386719),
                    'corey': np.float32(188.8341217),
                    'alt': np.float32(1.22173047),
                    'az': np.float32(3.14159274)
                },
                'telescope': {
                    'alt': np.float32(1.2217305),
                    'az': np.float32(3.1415927),
                    'position': np.array([-70.93, -52.07, 43.0])
                }
            },
            2: {
                'image_0': np.float32(3.4182658),
                'time_0': np.float32(26.897005),
                'labels': {
                    'energy': np.float32(0.12193353),
                    'corex': np.float32(-36.47265244),
                    'corey': np.float32(-294.10467529),
                    'alt': np.float32(1.22173047),
                    'az': np.float32(3.14159274)
                },
                'telescope': {
                    'alt': np.float32(1.2217305),
                    'az': np.float32(3.1415927),
                    'position': np.array([-70.93, -52.07, 43.0])
                }
            },
        }

        self.energy_filter_parameters = {'energy': [0.1, np.inf], 'filter_only_gammas': True}
        self.energy_filter_true_events = 7
        self.group_by_image_energy = {
            1: {
                'image_0': np.float32(3.4182658),
                'time_0': np.float32(26.897005),
            }
        }

        self.intensity_filter_parameters = {'intensity': [500, np.inf], 'cleaning': True,
                                            'picture_thresh': 8, 'boundary_thresh': 4,
                                            'keep_isolated_pixels': False, 'min_number_picture_neighbors': 1
                                            }

        self.group_by_image_intensity = {
            1: {
                'image_0': np.float32(2.447867),
                'time_0': np.float32(7.753113),
            }
        }

        self.intensity_lstchain_filter_parameters = {'intensity': [500, np.inf], 'dl1': True}

        self.group_by_image_intensity_energy = {
            1: {
                'image_0': np.float32(2.447867),
                'time_0': np.float32(7.753113),
            }
        }

        self.len_trig_energies = 17

    def test_mono_memory(self):

        dataset = dsets.MemoryLSTDataset(self.data_file, self.camera_type, 'image', self.targets, self.particle_dict,
                                         use_time=True,  subarray=self.subarray)
        sample_0 = dataset[0]
        assert sample_0['image'][0, 0] == self.group_by_image[0]['image_0']
        assert sample_0['image'][1, 0] == self.group_by_image[0]['time_0']
        assert np.isclose(sample_0['label']['energy'], np.log10(self.group_by_image[0]['labels']['energy']))
        assert np.isclose(sample_0['label']['impact'][0], (self.group_by_image[0]['labels']['corex'] -
                                                           self.group_by_image[0]['telescope']['position'][0])/1000)
        assert np.isclose(sample_0['label']['impact'][1], (self.group_by_image[0]['labels']['corey'] -
                                                           self.group_by_image[0]['telescope']['position'][1]) / 1000)
        assert np.isclose(sample_0['label']['direction'][0], (self.group_by_image[0]['labels']['alt'] -
                                                              self.group_by_image[0]['telescope']['alt']))
        assert np.isclose(sample_0['label']['direction'][1], (self.group_by_image[0]['labels']['az'] -
                                                              self.group_by_image[0]['telescope']['az']))

        sample_2 = dataset[2]

        assert sample_2['image'][0, 0] == self.group_by_image[2]['image_0']
        assert sample_2['image'][1, 0] == self.group_by_image[2]['time_0']
        assert np.isclose(sample_2['label']['energy'], np.log10(self.group_by_image[2]['labels']['energy']))
        assert np.isclose(sample_2['label']['impact'][0], (self.group_by_image[2]['labels']['corex'] -
                                                            self.group_by_image[2]['telescope']['position'][0]) / 1000)
        assert np.isclose(sample_2['label']['impact'][1], (self.group_by_image[2]['labels']['corey'] -
                                                            self.group_by_image[2]['telescope']['position'][1]) / 1000)

        assert np.isclose(sample_2['label']['direction'][0], (self.group_by_image[2]['labels']['alt'] -
                                                               self.group_by_image[2]['telescope']['alt']))
        assert np.isclose(sample_2['label']['direction'][1], (self.group_by_image[2]['labels']['az'] -
                                                               self.group_by_image[2]['telescope']['az']))

    def test_mono_memory_test_mode(self):

        dataset = dsets.MemoryLSTDataset(self.data_file, self.camera_type, 'image', self.targets, self.particle_dict,
                                         use_time=True, train=False,  subarray=self.subarray)
        sample_0 = dataset[0]
        assert sample_0['image'][0, 0] == self.group_by_image[0]['image_0']
        assert sample_0['image'][1, 0] == self.group_by_image[0]['time_0']
        assert np.isclose(sample_0['dl1_params']['mc_energy'], self.group_by_image[0]['labels']['energy'])
        assert np.isclose(sample_0['dl1_params']['mc_core_x'], self.group_by_image[0]['labels']['corex']/1000)
        assert np.isclose(sample_0['dl1_params']['mc_alt'], self.group_by_image[0]['labels']['alt'])

        sample_2 = dataset[2]

        assert sample_2['image'][0, 0] == self.group_by_image[2]['image_0']
        assert sample_2['image'][1, 0] == self.group_by_image[2]['time_0']
        assert np.isclose(sample_2['dl1_params']['mc_energy'], self.group_by_image[2]['labels']['energy'])
        assert np.isclose(sample_2['dl1_params']['mc_core_x'], self.group_by_image[2]['labels']['corex']/1000)
        assert np.isclose(sample_2['dl1_params']['mc_alt'], self.group_by_image[2]['labels']['alt'])

    def test_mono_file(self):

        dataset = dsets.FileLSTDataset(self.data_file, self.camera_type, 'image', self.targets, self.particle_dict,
                                       use_time=True,  subarray=self.subarray)

        sample_0 = dataset[0]
        assert sample_0['image'][0, 0] == self.group_by_image[0]['image_0']
        assert sample_0['image'][1, 0] == self.group_by_image[0]['time_0']
        assert np.isclose(sample_0['label']['energy'], np.log10(self.group_by_image[0]['labels']['energy']))
        assert np.isclose(sample_0['label']['impact'][0], (self.group_by_image[0]['labels']['corex'] -
                                                           self.group_by_image[0]['telescope']['position'][0]) / 1000)
        assert np.isclose(sample_0['label']['impact'][1], (self.group_by_image[0]['labels']['corey'] -
                                                           self.group_by_image[0]['telescope']['position'][1]) / 1000)
        assert np.isclose(sample_0['label']['direction'][0], (self.group_by_image[0]['labels']['alt'] -
                                                              self.group_by_image[0]['telescope']['alt']))
        assert np.isclose(sample_0['label']['direction'][1], (self.group_by_image[0]['labels']['az'] -
                                                              self.group_by_image[0]['telescope']['az']))

        sample_2 = dataset[2]

        assert sample_2['image'][0, 0] == self.group_by_image[2]['image_0']
        assert sample_2['image'][1, 0] == self.group_by_image[2]['time_0']
        assert np.isclose(sample_2['label']['energy'], np.log10(self.group_by_image[2]['labels']['energy']))
        assert np.isclose(sample_2['label']['impact'][0], (self.group_by_image[2]['labels']['corex'] -
                                                            self.group_by_image[2]['telescope']['position'][0]) / 1000)
        assert np.isclose(sample_2['label']['impact'][1], (self.group_by_image[2]['labels']['corey'] -
                                                            self.group_by_image[2]['telescope']['position'][1]) / 1000)

        assert np.isclose(sample_2['label']['direction'][0], (self.group_by_image[2]['labels']['alt'] -
                                                               self.group_by_image[2]['telescope']['alt']))
        assert np.isclose(sample_2['label']['direction'][1], (self.group_by_image[2]['labels']['az'] -
                                                               self.group_by_image[2]['telescope']['az']))

    def test_energy_filter_file(self):

        dataset_mono = dsets.FileLSTDataset(self.data_file, self.camera_type, 'image', self.targets,
                                            self.particle_dict, use_time=True,  subarray=self.subarray)
        dataset_mono.filter_event({utils.energyband_filter: self.energy_filter_parameters})
        assert len(dataset_mono.dl1_params['mc_energy']) == self.energy_filter_true_events

        sample_1 = dataset_mono[1]

        assert sample_1['image'][0, 0] == self.group_by_image_energy[1]['image_0']
        assert sample_1['image'][1, 0] == self.group_by_image_energy[1]['time_0']

    def test_energy_filter_memory(self):

        dataset_mono = dsets.MemoryLSTDataset(self.data_file, self.camera_type, 'image', self.targets,
                                              self.particle_dict, use_time=True,  subarray=self.subarray)
        dataset_mono.filter_event({utils.energyband_filter: self.energy_filter_parameters})
        assert len(dataset_mono.dl1_params['mc_energy']) == self.energy_filter_true_events

        sample_1 = dataset_mono[1]

        assert sample_1['image'][0, 0] == self.group_by_image_energy[1]['image_0']
        assert sample_1['image'][1, 0] == self.group_by_image_energy[1]['time_0']

    def test_intensity_filter_memory(self):

        dataset_mono = dsets.MemoryLSTDataset(self.data_file, self.camera_type, 'image', self.targets,
                                              self.particle_dict, use_time=True,  subarray=self.subarray)
        dataset_mono.filter_image({utils.intensity_filter: self.intensity_filter_parameters})
        sample_0 = dataset_mono[1]
        assert sample_0['image'][0, 0] == self.group_by_image_intensity[1]['image_0']
        assert sample_0['image'][1, 0] == self.group_by_image_intensity[1]['time_0']

    def test_intensity_filter_file(self):

        dataset_mono = dsets.FileLSTDataset(self.data_file, self.camera_type, 'image', self.targets,
                                            self.particle_dict, use_time=True,  subarray=self.subarray)
        dataset_mono.filter_image({utils.intensity_filter: self.intensity_filter_parameters})
        sample_0 = dataset_mono[1]
        assert sample_0['image'][0, 0] == self.group_by_image_intensity[1]['image_0']
        assert sample_0['image'][1, 0] == self.group_by_image_intensity[1]['time_0']

    def test_intensity_lstchain_filter_memory(self):

        dataset_mono = dsets.MemoryLSTDataset(self.data_file, self.camera_type, 'image', self.targets,
                                              self.particle_dict, use_time=True,  subarray=self.subarray)
        dataset_mono.filter_image({utils.intensity_filter: self.intensity_lstchain_filter_parameters})
        sample_0 = dataset_mono[1]
        assert sample_0['image'][0, 0] == self.group_by_image_intensity[1]['image_0']
        assert sample_0['image'][1, 0] == self.group_by_image_intensity[1]['time_0']

    def test_intensity_lstchain_filter_file(self):

        dataset_mono = dsets.FileLSTDataset(self.data_file, self.camera_type, 'image', self.targets,
                                            self.particle_dict, use_time=True,  subarray=self.subarray)
        dataset_mono.filter_image({utils.intensity_filter: self.intensity_lstchain_filter_parameters})
        sample_0 = dataset_mono[1]
        assert sample_0['image'][0, 0] == self.group_by_image_intensity[1]['image_0']
        assert sample_0['image'][1, 0] == self.group_by_image_intensity[1]['time_0']

    def test_intensity_energy_filter_memory(self):

        dataset_mono = dsets.MemoryLSTDataset(self.data_file, self.camera_type, 'image', self.targets,
                                              self.particle_dict, use_time=True,  subarray=self.subarray)
        dataset_mono.filter_image({utils.intensity_filter: self.intensity_filter_parameters})
        dataset_mono.filter_event({utils.energyband_filter: self.energy_filter_parameters})

        sample_2 = dataset_mono[1]
        assert sample_2['image'][0, 0] == self.group_by_image_intensity_energy[1]['image_0']
        assert sample_2['image'][1, 0] == self.group_by_image_intensity_energy[1]['time_0']

    def test_intensity_energy_filter_file(self):

        dataset_mono = dsets.FileLSTDataset(self.data_file, self.camera_type, 'image', self.targets,
                                              self.particle_dict, use_time=True,  subarray=self.subarray)
        dataset_mono.filter_image({utils.intensity_filter: self.intensity_filter_parameters})
        dataset_mono.filter_event({utils.energyband_filter: self.energy_filter_parameters})

        sample_2 = dataset_mono[1]
        assert sample_2['image'][0, 0] == self.group_by_image_intensity_energy[1]['image_0']
        assert sample_2['image'][1, 0] == self.group_by_image_intensity_energy[1]['time_0']

    def test_subarray(self):
        dataset_mono = dsets.MemoryLSTDataset(self.data_file, self.camera_type, 'image', self.targets,
                                              self.particle_dict, use_time=True,  subarray=self.subarray)
        assert len(dataset_mono.trig_energies) == self.len_trig_energies
        assert len(dataset_mono.images) == self.len_trig_energies

    # TODO test stereo


class TestLSTRealDataset(unittest.TestCase):

    def setUp(self) -> None:
        self.data_file = os.path.join(THIS_DIR, '../../share/data/real_data/dl1_realdata_example.h5')
        self.camera_type = 'LST_LSTCam'
        self.subarray = [1]
        self.group_by_image = {
            0: {
                'image_0': np.float32(2.8471088),
                'time_0': np.float32(8.674426),
                'telescope': {
                    'alt': np.float32(1.25764907),
                    'az': np.float32(0.80768447),
                    'position': np.array([50., 50., 16.])
                }
            },
            2: {
                'image_0': np.float32(0.822368),
                'time_0': np.float32(31.549051),
                'telescope': {
                    'alt': np.float32(1.25764908),
                    'az': np.float32(0.80768444),
                    'position': np.array([50., 50., 16.])
                }
            },
        }

        self.intensity_filter_parameters = {'intensity': [0, 250], 'cleaning': True,
                                            'picture_thresh': 8, 'boundary_thresh': 4,
                                            'keep_isolated_pixels': False, 'min_number_picture_neighbors': 1
                                            }

        self.group_by_image_intensity = {
            0: {
                'image_0': np.float32(3.4779184),
                'time_0': np.float32(19.180153),
            }
        }

        self.intensity_lstchain_filter_parameters = {'intensity': [0, 250], 'dl1': True}

    def test_mono_memory(self):

        dataset = dsets.MemoryLSTDataset(self.data_file, self.camera_type, 'image',
                                         use_time=True,  subarray=self.subarray)
        assert dataset.trig_energies is None

        sample_0 = dataset[0]
        assert sample_0['image'][0, 0] == self.group_by_image[0]['image_0']
        assert sample_0['image'][1, 0] == self.group_by_image[0]['time_0']

        sample_2 = dataset[2]

        assert sample_2['image'][0, 0] == self.group_by_image[2]['image_0']
        assert sample_2['image'][1, 0] == self.group_by_image[2]['time_0']

    def test_mono_memory_test_mode(self):

        dataset = dsets.MemoryLSTDataset(self.data_file, self.camera_type, 'image',
                                         use_time=True, train=False,  subarray=self.subarray)
        sample_0 = dataset[0]
        assert sample_0['image'][0, 0] == self.group_by_image[0]['image_0']
        assert sample_0['image'][1, 0] == self.group_by_image[0]['time_0']

        sample_2 = dataset[2]

        assert sample_2['image'][0, 0] == self.group_by_image[2]['image_0']
        assert sample_2['image'][1, 0] == self.group_by_image[2]['time_0']

    def test_mono_file(self):

        dataset = dsets.FileLSTDataset(self.data_file, self.camera_type, 'image',
                                       use_time=True,  subarray=self.subarray)
        sample_0 = dataset[0]
        assert sample_0['image'][0, 0] == self.group_by_image[0]['image_0']
        assert sample_0['image'][1, 0] == self.group_by_image[0]['time_0']

        sample_2 = dataset[2]

        assert sample_2['image'][0, 0] == self.group_by_image[2]['image_0']
        assert sample_2['image'][1, 0] == self.group_by_image[2]['time_0']

    def test_intensity_filter_memory(self):

        dataset_mono = dsets.MemoryLSTDataset(self.data_file, self.camera_type, 'image',
                                              use_time=True,  subarray=self.subarray)
        dataset_mono.filter_image({utils.intensity_filter: self.intensity_filter_parameters})
        sample_0 = dataset_mono[0]
        assert sample_0['image'][0, 0] == self.group_by_image_intensity[0]['image_0']
        assert sample_0['image'][1, 0] == self.group_by_image_intensity[0]['time_0']

    def test_intensity_filter_file(self):

        dataset_mono = dsets.FileLSTDataset(self.data_file, self.camera_type, 'image',
                                            use_time=True,  subarray=self.subarray)
        dataset_mono.filter_image({utils.intensity_filter: self.intensity_filter_parameters})
        sample_0 = dataset_mono[0]
        assert sample_0['image'][0, 0] == self.group_by_image_intensity[0]['image_0']
        assert sample_0['image'][1, 0] == self.group_by_image_intensity[0]['time_0']

    def test_intensity_lstchain_filter_memory(self):

        dataset_mono = dsets.MemoryLSTDataset(self.data_file, self.camera_type, 'image',
                                              use_time=True,  subarray=self.subarray)
        dataset_mono.filter_image({utils.intensity_filter: self.intensity_lstchain_filter_parameters})
        sample_0 = dataset_mono[0]
        assert sample_0['image'][0, 0] == self.group_by_image_intensity[0]['image_0']
        assert sample_0['image'][1, 0] == self.group_by_image_intensity[0]['time_0']

    def test_intensity_lstchain_filter_file(self):

        dataset_mono = dsets.FileLSTDataset(self.data_file, self.camera_type, 'image',
                                            use_time=True,  subarray=self.subarray)
        dataset_mono.filter_image({utils.intensity_filter: self.intensity_lstchain_filter_parameters})
        sample_0 = dataset_mono[0]
        assert sample_0['image'][0, 0] == self.group_by_image_intensity[0]['image_0']
        assert sample_0['image'][1, 0] == self.group_by_image_intensity[0]['time_0']


    # TODO test stereo


if __name__ == '__main__':
    unittest.main()
