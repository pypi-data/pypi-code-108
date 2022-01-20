import multiprocessing as mp

import tables
import numpy as np
import torch
from torch.utils.data import Dataset
from astropy.table import Table
import astropy.units as u
from ctapipe.instrument import CameraGeometry
from ctapipe.image import tailcuts_clean
from lstchain.io.io import read_simu_info_merged_hdf5
from lstchain.io.io import dl1_images_lstcam_key, dl1_params_lstcam_key
from dl1_data_handler.image_mapper import ImageMapper



DL1_SUBARRAY_TRIGGER_KEY = 'dl1/event/subarray/trigger'
DL1_SUBARRAY_LAYOUT = 'configuration/instrument/subarray/layout'

class WrongGeometryError(Exception):
    pass

class MockLSTDataset(Dataset):

    def __init__(self, hdf5_file_path, camera_type, group_by, targets=None, particle_dict=None, use_time=False, train=True,
                 subarray=None, transform=None, target_transform=None):

        self.images = np.random.rand(50, 1855).astype(np.float32)
        self.times = np.random.rand(50, 1855).astype(np.float32)

        self.particle_dict = {0: 0, 101: 1}

        self.camera_type = 'LST_LSTCam'
        self.group_by = 'image'
        self.original_geometry = CameraGeometry.from_name('LSTCam')
        self.camera_geometry = CameraGeometry.from_name('LSTCam')
        self.simu = True
        self.dl1_params = {
            'event_id': np.arange(50),
            'mc_type': np.random.choice([101, 0], size=50),
            'mc_energy': np.random.rand(50).astype(np.float32),
            'log_mc_energy': np.random.rand(50).astype(np.float32),
            'mc_alt_tel': np.full(50, np.deg2rad(70), dtype=np.float32),
            'mc_az_tel': np.full(50, np.deg2rad(180), dtype=np.float32),
            'mc_alt': np.random.rand(50).astype(np.float32),
            'mc_az': np.random.rand(50).astype(np.float32),
            'mc_core_x': np.random.rand(50).astype(np.float32),
            'mc_core_y': np.random.rand(50).astype(np.float32),
            'tel_id': np.random.rand(50).astype(np.float32),
            'tel_pos_x': np.random.rand(50).astype(np.float32),
            'tel_pos_y': np.random.rand(50).astype(np.float32),
        }

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        data = np.stack([self.images[idx], self.times[idx]])
        dl1_params = {n: p[idx] for n, p in self.dl1_params.items()}
        labels = {'energy': np.array([dl1_params['log_mc_energy']], dtype=np.float32),
                  'impact': np.array([dl1_params['mc_core_x'] - dl1_params['tel_pos_x'],
                                      dl1_params['mc_core_y'] - dl1_params['tel_pos_y']], dtype=np.float32),
                  'direction': np.array([dl1_params['mc_alt'] - dl1_params['mc_alt_tel'],
                                         dl1_params['mc_az'] - dl1_params['mc_az_tel']], dtype=np.float32),
                  'class':  self.particle_dict.get(dl1_params['mc_type'], -1)
                  }
        sample = {'image': data,
                  'dl1_params': dl1_params,
                  'label': labels}

        return sample

    def filter_image(self, filter_dict):
        pass

    def filter_event(self, filter_dict):
        pass


class BaseLSTDataset(Dataset):
    """camera simulation dataset for lstchain DL1 hdf5 files. """

    def __init__(self, hdf5_file_path, camera_type, group_by, targets=None, particle_dict=None, use_time=False,
                 train=True,
                 subarray=None, transform=None, target_transform=None):
        """
        Parameters
        ----------
            hdf5_file_path (str): path to hdf5 file containing the data
            camera_type (str) : name of the camera used (e.g. camera_type='LST_LSTCam)
            group_by (str): the way to group images in the dataset (e.g. 'event_triggered_tels' :
            by event only for telescopes which triggered)
            targets (list): the targets to include in the sample
            particle_dict (dict): Dictionary of particle types
            use_time (bool, optional): whether or not include the time peak in the sample
            train (bool, optional): defines the dataset mode (train or test)
            subarray (Array): array of telescopes ids that defines the subarray used
            transform (callable, optional): Optional transform to be applied on a sample
            target_transform (callable, optional): Optional transform to be applied on a sample
        """
        self.hdf5_file_path = hdf5_file_path
        self.hdf5_file = None
        self.camera_type = camera_type
        if not self.camera_type == 'LST_LSTCam':
            WrongGeometryError("passed camera_type should be LST_LSTCam")

        self.targets = targets
        self.particle_dict = particle_dict
        self.transform = transform
        self.target_transform = target_transform
        self.use_time = use_time
        self.train = train

        self.images = None
        self.times = None
        self.filtered_indices = None
        self.lstchain_version = None
        self.simu = True

        group_by_options = ['image', 'event_all_tels', 'event_triggered_tels']

        assert group_by in group_by_options, '{} is not a suitable group option. Must be in {}'.format(group_by,
                                                                                                       group_by_options)

        self.group_by = group_by

        # LSTCam is used as default geometry at the moment.
        # all data (MC and real) are converted to this geom.
        self.camera_geometry = CameraGeometry.from_name('LSTCam')
        rot_angle = self.camera_geometry.pix_rotation
        # We need to rotate the camera for ImageMapper
        self.camera_geometry.rotate(rot_angle)

        geom_table = Table.read(hdf5_file_path, path='/configuration/instrument/telescope/camera/geometry_LSTCam')
        self.original_geometry = CameraGeometry.from_table(geom_table)
        # Rotate the original geometry as well to align both geometries
        self.original_geometry.rotate(self.original_geometry.pix_rotation)

        self.inj_table = self.original_geometry.position_to_pix_index(self.camera_geometry.pix_x,
                                                                      self.camera_geometry.pix_y)

        # Load run config
        try:
            self.run_config = {'mcheader': read_simu_info_merged_hdf5(self.hdf5_file_path)}
        except IndexError as e:
            self.simu = False
            self.run_config = {}
        if self.simu:
            assert particle_dict is not None, 'You must define a particle dictionary for MC dataset !'
            self.targets = [] if self.targets is None else self.targets
        self.run_config['metadata'] = {}

        with tables.File(hdf5_file_path, 'r') as hdf5_file:
            for attr in hdf5_file.root._v_attrs._f_list('user'):
                self.run_config['metadata'][attr] = hdf5_file.root._v_attrs[attr]

            self.dl1_params = hdf5_file.root[dl1_params_lstcam_key][:]
            self.dl1_param_names = hdf5_file.root[dl1_params_lstcam_key].colnames

            # image related infos
            self.filtered_indices = np.arange(len(hdf5_file.root[dl1_images_lstcam_key]), dtype=int)

            # LST subarray
            layout = hdf5_file.root[DL1_SUBARRAY_LAYOUT][:]
            lst_layout_mask = layout['name'] == b'LST'
            self.layout_tel_ids = layout['tel_id'][lst_layout_mask]

            # Keep a copy of triggered energies for gammaboard
            if self.simu:
                _, indices = np.unique(self.dl1_params[:]['event_id'], return_index=True)
                self.trig_energies = self.dl1_params['mc_energy'][indices]
                self.trig_tels = hdf5_file.root[DL1_SUBARRAY_TRIGGER_KEY][:]['tels_with_trigger']
            else:
                self.trig_energies = None
                self.trig_tels = np.full((len(self.dl1_params), 6), False)
                self.trig_tels[:, np.searchsorted(layout['tel_id'], self.dl1_params[
                    'tel_id'])] = True  # TODO fix when real data has several tels
            # Select sub-subarray
            if subarray is not None:
                assert np.in1d(subarray, self.layout_tel_ids).all(), 'All the telescopes of the subarray must be LSTs'
                self.layout_tel_ids = subarray
            subarray_mask = np.any(self.trig_tels[:, np.searchsorted(layout['tel_id'], self.layout_tel_ids)], axis=1)
            if self.trig_energies is not None:
                self.trig_energies = self.trig_energies[subarray_mask]
            event_mask = np.in1d(self.dl1_params['tel_id'], self.layout_tel_ids)
            self.dl1_params = self.dl1_params[event_mask]
            self.filtered_indices = self.filtered_indices[event_mask]

            # Load event info
            self.unique_event_ids = np.unique(self.dl1_params[:]['event_id'])

            if self.simu:
                # Turn distances into km
                self.dl1_params['mc_x_max'] /= 1000
                self.dl1_params['mc_core_x'] /= 1000
                self.dl1_params['mc_core_y'] /= 1000
            self.dl1_params['tel_pos_x'] /= 1000
            self.dl1_params['tel_pos_y'] /= 1000
            self.dl1_params['tel_pos_z'] /= 1000

        # setup the ImageMapper transform
        if self.transform is not None:
            for t in self.transform.transforms:
                if hasattr(t, 'setup_geometry'):
                    t.setup_geometry(self.camera_geometry)

    def __len__(self):
        if self.group_by == 'image':
            return len(self.filtered_indices)
        else:
            return len(self.unique_event_ids)

    def _get_sample(self, idx):
        if self.group_by == 'image':
            data_t = self._get_image_data(idx)
            data = np.stack(data_t) if self.use_time else data_t[0]
            dl1_params = self.dl1_params[idx]
        else:
            event_id = self.unique_event_ids[idx]
            filtered_images_ids = np.arange(len(self.dl1_params))[self.dl1_params['event_id'] == event_id]
            dl1_params = self.dl1_params[self.dl1_params['event_id'] == event_id]
            tel_ids = dl1_params['tel_id'] - 1  # telescope ids start from 1
            dl1_params = dl1_params[0] if dl1_params.ndim > 1 else dl1_params
            if self.group_by == 'event_all_tels':
                # We want as many images as telescopes
                images_ids = np.full(len(self.layout_tel_ids), -1)
                images_ids[tel_ids] = filtered_images_ids
            elif self.group_by == 'event_triggered_tels':
                images_ids = filtered_images_ids
            else:
                raise ValueError('group_by option has an incorrect value.')
            data_t = self._get_image_data(images_ids)
            if self.use_time:
                assert len(data_t) == 2, 'When using both charge and peakpos you need the same' \
                                         'amount of each'
                event_images = data_t[0]
                event_times = data_t[1]
                event_images = np.nan_to_num(event_images)
                event_times = np.nan_to_num(event_times)

                data = np.empty((event_images.shape[0] * 2, event_images.shape[1]), dtype=np.float32)
                data[0::2, :] = event_images
                data[1::2, :] = event_times
            else:
                data = data_t[0]

        dl1_parameters = {n: p for n, p in zip(self.dl1_param_names, dl1_params)}
        if self.train and self.simu:
            labels = {}
            for t in self.targets:
                if t == 'energy':
                    labels[t] = np.array([dl1_params['log_mc_energy']], dtype=np.float32)
                elif t == 'impact':
                    if self.group_by == 'image':
                        labels[t] = np.array([dl1_params['mc_core_x'] - dl1_params['tel_pos_x'],
                                              dl1_params['mc_core_y'] - dl1_params['tel_pos_y']], dtype=np.float32)
                    else:
                        labels[t] = np.array([dl1_params['mc_core_x'], dl1_params['mc_core_y']], dtype=np.float32)
                elif t == 'direction':
                    if self.group_by == 'image':
                        labels[t] = np.array([dl1_params['mc_alt'] - dl1_params['mc_alt_tel'],
                                              dl1_params['mc_az'] - dl1_params['mc_az_tel']], dtype=np.float32)
                    else:
                        labels[t] = np.array([dl1_params['mc_alt'], dl1_params['mc_az']], dtype=np.float32)
                elif t == 'xmax':
                    labels[t] = np.array([dl1_params['mc_x_max']])
                elif t == 'class':  # TODO replace by try except
                    labels[t] = self.particle_dict.get(dl1_params['mc_type'], -1)
                    if labels[t] == -1:
                        print(dl1_params['mc_type'])
                        print(self.hdf5_file_path)
                else:
                    raise ValueError('Unknown target')
        else:
            labels = None

        # We reogranize the pixels to match the 'LSTCam' geometry
        sample = {'image': data[..., self.inj_table]}
        if labels is not None:
            sample['label'] = labels
        sample['dl1_params'] = dl1_parameters

        if self.transform:
            sample['image'] = self.transform(sample['image'])
        if self.target_transform and labels is not None:
            sample['label'] = {t: self.target_transform(label) for t, label in sample['label'].items()}

        return sample

    def _get_image_data(self, idx):
        raise NotImplementedError

    def filter_event(self, filter_dict):
        filter_mask = np.full(len(self.dl1_params), True)
        for filter_func, params in filter_dict.items():
            filter_mask = filter_mask & filter_func(self, **params)
        # Apply filtering
        self._update_events(filter_mask)
        # update images
        self.update_images(filter_mask)

    def _update_events(self, filter_mask):
        self.dl1_params = self.dl1_params[filter_mask]
        self.unique_event_ids = np.unique(self.dl1_params[:]['event_id'])

    def _filter_image(self, filter_dict):
        filter_mask = np.full(len(self.images), True)
        for filter_func, params in filter_dict.items():
            filter_mask = filter_mask & filter_func(self, **params)
        # Apply filtering
        self.update_images(filter_mask)
        self._update_events(filter_mask)

    def update_images(self, image_mask):

        raise NotImplementedError

    def filter_image(self, filter_dict):

        raise NotImplementedError


class MemoryLSTDataset(BaseLSTDataset):

    def __init__(self, hdf5_file_path, camera_type, group_by, targets=None, particle_dict=None, use_time=False,
                 train=True,
                 subarray=None, transform=None, target_transform=None):

        super(MemoryLSTDataset, self).__init__(hdf5_file_path, camera_type, group_by, targets, particle_dict,
                                               use_time, train, subarray, transform, target_transform)

        with tables.File(hdf5_file_path, 'r') as hdf5_file:
            # Load images and peak times
            self.images = hdf5_file.root[dl1_images_lstcam_key].col('image').astype(np.float32)[self.filtered_indices]
            self.images = np.nan_to_num(self.images)
            if self.use_time:
                self.times = hdf5_file.root[dl1_images_lstcam_key].col('peak_time').astype(np.float32)[
                    self.filtered_indices]
                self.times = np.nan_to_num(self.times)

    def __getitem__(self, idx):
        return self._get_sample(idx)

    def _get_image_data(self, idx):
        if isinstance(idx, np.ndarray):
            data = np.zeros((len(idx), self.images.shape[1]))
            time = None
            if self.use_time:
                time = np.zeros((len(idx), self.times.shape[1]))
            for i, ind in enumerate(idx):
                if ind > -1:
                    indice = np.argwhere(self.filtered_indices == ind).item()
                    data[i] = self.images[indice]
                    if self.use_time:
                        time[i] = self.times[indice]
            data = (data,)
            if self.use_time:
                data += (time,)
        else:
            data = (self.images[idx],)
            if self.use_time:
                data += self.times[idx],
        return data

    def filter_image(self, filter_dict):
        self._filter_image(filter_dict)

    def update_images(self, image_mask):
        self.images = self.images[image_mask]
        if self.times is not None:
            self.times = self.times[image_mask]
        self.filtered_indices = np.arange(len(self.images))


class FileLSTDataset(BaseLSTDataset):

    def __init__(self, hdf5_file_path, camera_type, group_by, targets=None, particle_dict=None, use_time=False,
                 train=True,
                 subarray=None, transform=None, target_transform=None):

        super(FileLSTDataset, self).__init__(hdf5_file_path, camera_type, group_by, targets, particle_dict,
                                             use_time, train, subarray, transform, target_transform)

    def __getitem__(self, idx):
        if self.hdf5_file is None:
            self.hdf5_file = tables.File(self.hdf5_file_path, 'r')
        return self._get_sample(idx)

    def _get_image_data(self, idx):
        image_id = self.filtered_indices[idx]
        if isinstance(image_id, np.ndarray):
            image_size = self.hdf5_file.root[dl1_images_lstcam_key].col('image').shape[1]
            data = np.zeros((len(image_id), image_size))
            time = None
            if self.use_time:
                time = np.zeros((len(image_id), image_size))
            for i, ind in enumerate(image_id):
                if ind > -1:
                    data[i] = np.nan_to_num(
                        self.hdf5_file.root[dl1_images_lstcam_key].col('image')[ind].astype(np.float32))
                    if self.use_time:
                        time[i] = np.nan_to_num(
                            self.hdf5_file.root[dl1_images_lstcam_key].col('peak_time')[ind].astype(np.float32))
            data = (data,)
            if self.use_time:
                data += time
        else:
            data = np.nan_to_num(self.hdf5_file.root[dl1_images_lstcam_key].col('image')[image_id].astype(np.float32)),
            if self.use_time:
                time = np.nan_to_num(
                    self.hdf5_file.root[dl1_images_lstcam_key].col('peak_time')[image_id].astype(np.float32))
                data += time,
        return data

    def filter_image(self, filter_dict):
        self._open_file()
        self._filter_image(filter_dict)
        self._close_file()

    def update_images(self, image_mask):
        self.filtered_indices = self.filtered_indices[image_mask]

    def _open_file(self):
        if self.hdf5_file is None:
            self.hdf5_file = tables.File(self.hdf5_file_path, 'r')
            self.images = np.nan_to_num(self.hdf5_file.root[dl1_images_lstcam_key].col('image')[self.filtered_indices])
            self.times = np.nan_to_num(
                self.hdf5_file.root[dl1_images_lstcam_key].col('peak_time')[self.filtered_indices])

    def _close_file(self):
        if self.hdf5_file is not None:
            self.hdf5_file.close()
            self.hdf5_file = None
            self.images = None
            self.times = None


class NumpyDataset(Dataset):

    def __init__(self, data, labels, transform=None, target_transform=None):
        self.images = data
        self.labels = labels
        self.transform = transform
        self.target_transform = target_transform

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, item):

        if self.transform:
            self.images[item] = self.transform(self.images[item])
        if self.target_transform:
            self.labels[item] = self.target_transform(self.labels[item])

        return self.images[item], self.labels[item]


class HDF5Dataset(Dataset):
    """Loads data in a Dataset from a HDF5 file.

    Args:
        path (str): The path to the HDF5 file.
        transform (callable, optional): A callable or a composition of callable to be applied to the data.
        target_transform (callable, optional): A callable or a composition of callable to be applied to the labels.
    """

    def __init__(self, path, camera_type, transform=None, target_transform=None, telescope_transform=None):
        with tables.File(path, 'r') as f:
            self.images = f.root['images'][:][()]
            self.labels = f.root['labels'][:][()]
        self.transform = transform
        self.target_transform = target_transform
        self.camera_type = camera_type

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, item):
        image, label = self.images[item], self.labels[item]
        if self.transform:
            image = self.transform(image)
        if self.target_transform:
            label = self.transform(label)

        return {'image': image, 'label': label}


# Transforms classes

class TransformIACT:

    def setup_geometry(self, camera_geometry):
        raise NotImplementedError


class ResampleImage(TransformIACT):
    """
    Resample an hexagonal image with DL1 Data Handler Image Mapper
    The class needs to be instantiated first to be passed to a Dataset class but can be setup later when the camera
    information is available to the user
    """

    def __init__(self, mapping, output_size):
        self.camera = None
        self.image_mapper = None
        self.mapping = mapping
        self.output_size = output_size

    def setup_geometry(self, camera_geometry):
        pix_pos = np.array([camera_geometry.pix_x.to_value(u.m),
                            camera_geometry.pix_y.to_value(u.m),
                            ])
        self.camera = camera_geometry.camera_name
        self._setup_image_mapper(pix_pos)

    def _setup_image_mapper(self, pix_pos):
        self.image_mapper = ImageMapper(pixel_positions={self.camera: pix_pos},
                                        camera_types=[self.camera],
                                        mapping_method={self.camera: self.mapping},
                                        interpolation_image_shape={self.camera: self.output_size}
                                        )

    def __call__(self, data):
        mapped_data = self.image_mapper.map_image(data.T, self.camera)
        return mapped_data.T


class RescaleCharge(object):

    def __init__(self, scale):
        self.scale = scale

    def __call__(self, data):
        if data.ndim == 1:
            data = data * self.scale
        elif data.ndim == 2:
            data[0] = data[0] * self.scale
        return data


class AddPoissonNoise(object):

    def __init__(self, rate):
        self.poisson = torch.distributions.poisson.Poisson(rate)

    def __call__(self, data):
        if data.ndim == 1:
            data = data + self.poisson.sample(sample_shape=torch.Size(list(data.shape))).numpy()
        elif data.ndim == 2:
            data[0] = data[0] + self.poisson.sample(sample_shape=torch.Size(list(data[0].shape))).numpy()
        return data


class Unsqueeze(object):
    """Unsqueeze a tensor"""

    def __call__(self, data):
        data.unsqueeze_(0)
        return data


class NumpyToTensor(object):
    """Convert a numpy array to a tensor"""

    def __call__(self, data):
        data = torch.tensor(data)
        return data


class RotateImage(object):
    """Rotate telescope image based on rotated indices"""

    def __init__(self, rotated_indices):
        self.rotated_indices = rotated_indices

    def __call__(self, data):
        assert data.shape[-1] == self.rotated_indices.shape[0], 'The length of rotated indices must match the size ' \
                                                                'of the image to rotate. '
        return data[..., self.rotated_indices]


class NormalizePixel(object):

    def __init__(self, max_pix):
        self.max = max_pix

    def __call__(self, data):
        return data / self.max


class CleanImages(TransformIACT):

    def __init__(self, **opts):
        self.opts = opts
        self.camera_geometry = None

    def setup_geometry(self, camera_geometry):
        self.camera_geometry = camera_geometry

    def __call__(self, data):
        image = data if data.ndim == 1 else data[0]
        clean_mask = tailcuts_clean(self.camera_geometry, image, **self.opts)

        return data * clean_mask


# Augment data functions

def augment_via_duplication(datasets, scale, num_workers):
    """
    Augment data by duplicating events based on the inverse detected energies distribution
    Parameters
    ----------
    datasets (list): list of Subsets
    scale (float): the scale to constrain the maximum duplication factor
    num_workers (int): number of processes to use

    Returns
    -------

    """

    def get_factor(energy, scale):
        fitlog = 1.19 * (2.59 - energy) * (1 - np.exp(-2.91 - energy))
        p = 1 / (10 ** fitlog) * 1 / (1 / (10 ** fitlog)).min()
        return np.floor(1 + scale * np.log10(p)).astype(np.int)

    def process_subset():
        torch.set_num_threads(1)
        while True:
            if input_queue.empty():
                break
            else:
                sub = input_queue.get()
                factors = get_factor(np.log10(sub.dataset.energies), scale)
                augmented_ids = np.repeat(np.arange(len(sub.dataset)), factors)
                sub.indices = augmented_ids[np.in1d(augmented_ids, sub.indices)]
                new_datasets.append(sub)

    input_queue = mp.Queue()
    for subset in datasets:
        input_queue.put(subset)
    manager = mp.Manager()
    new_datasets = manager.list()
    workers = [mp.Process(target=process_subset) for _ in range(num_workers)]
    for w in workers:
        w.start()
    input_queue.close()
    for w in workers:
        w.join()
    return list(new_datasets)
