import os
import logging
import inspect
import csv
import collections
import json
import pkg_resources

import numpy as np
import tables
import torch
from ctapipe.image import tailcuts_clean, leakage_parameters, hillas_parameters
from ctaplot.ana import angular_separation_altaz
from . import version
from .constants import GAMMA_ID
from astropy.utils import deprecated


def browse_folder(data_folder, extension=None):
    """
    Browse folder given to find hdf5 files
    Parameters
    ----------
    data_folder (string)
    extension (string)

    Returns
    -------
    set of hdf5 files
    """
    logger = logging.getLogger(__name__)
    if extension is None:
        extension = ['.hdf5', '.h5']
    try:
        assert isinstance(extension, list)
    except AssertionError as e:
        logger.exception('extension must be provided as a list')
        raise e
    logger.debug('browse folder')
    file_set = set()
    for dirname, dirnames, filenames in os.walk(data_folder):
        logger.debug('found folders : {}'.format(dirnames))
        logger.debug('in {}'.format(dirname))
        logger.debug('found files : {}'.format(filenames))
        for file in filenames:
            filename, ext = os.path.splitext(file)
            if ext in extension:
                file_set.add(dirname+'/'+file)
    return file_set


def prepare_experiment_folder(main_directory, experiment_name):
    """
    Prepare experiment folder and check if already exists
    Parameters
    ----------
    main_directory (string)
    experiment_name (string)

    Returns
    -------

    """
    logger = logging.getLogger(__name__)
    experiment_directory = main_directory + '/' + experiment_name + '/'
    if not os.path.exists(experiment_directory):
        os.makedirs(experiment_directory)
        os.chmod(experiment_directory, 0o775)
    else:
        logger.info('The experiment {} already exists !'.format(experiment_name))
    logger.info('Experiment directory: %s ' % experiment_directory)


def prepare_gammaboard_folder(main_directory, experiment_name):
    """
    Prepare tensorboard run folder for the experiment
    Parameters
    ----------
    main_directory (string)
    experiment_name (string)

    Returns
    -------

    """
    logger = logging.getLogger(__name__)
    test_directory = main_directory + '/gammaboard/' + experiment_name
    if not os.path.exists(test_directory):
        os.makedirs(test_directory)
        os.chmod(test_directory, 0o775)
    logger.debug('Gammaboard runs directory: {} '.format(test_directory))
    return test_directory


def record_experiment(experiment):
    """
    Record the main parameters of the experiment in a file containing all the experiments

    Parameters
    ----------
    experiment (Experiment) : experiment

    Returns
    -------

    """
    with open(experiment.main_directory + '/experiments.csv', 'a', newline='') as f:
        writer = csv.writer(f)

        optim = {
            key: experiment.optimizer_dic[key].__name__
            for key in experiment.optimizer_dic.keys()
        }

        criterion = {
            task: param['loss'].__name__
            if inspect.isfunction(param['loss'])
            else param['loss'].__class__.__name__
            for task, param in experiment.targets.items()
        }

        writer.writerow([experiment.experiment_name,
                         experiment.model_net.__name__,
                         optim,
                         experiment.optimizer_parameters,
                         criterion,
                         experiment.batch_size,
                         experiment.nepochs,
                         experiment.image_filter,
                         experiment.event_filter,
                         experiment.files_folders])


def resume_model(model, path):
    """
    Resume the model with the one stored in the path.
    https://discuss.pytorch.org/t/how-to-load-part-of-pre-trained-model/1113/16
    Parameters
    ----------
    model (torch.Module)
    path (string)

    Returns
    -------

    """
    pretrained_dict = torch.load(f=path,  map_location=lambda storage, loc: storage)
    model_dict = model.state_dict()
    # 1. filter out unnecessary keys (not in the model)
    pretrained_dict = {
        k: v
        for k, v in pretrained_dict.items()
        if k in model_dict and 'mask_' not in k and 'indices_' not in k
    }

    # 2. overwrite entries in the existing state dict
    model_dict.update(pretrained_dict)
    # 3. load the new state dict
    model.load_state_dict(model_dict)


def find_datafiles(data_folders, files_max_number=0):
    """
    Find datafiles in the folders specified
    Parameters
    ----------
    data_folders (list): the folders where the data are stored
    files_max_number (int, optional): the maximum number of files to keep per folder

    Returns
    -------

    """
    logger = logging.getLogger(__name__)
    logger.debug('data folders : {}'.format(data_folders))
    # We can have several folders
    datafiles = set()
    for folder in data_folders:
        logger.debug('data folder : {}'.format(folder))
        dataf = list(browse_folder(folder))
        dataf.sort()
        if files_max_number and 0 < files_max_number <= len(dataf):
            dataf = dataf[0:files_max_number]
        dataf = set(dataf)
        datafiles.update(dataf)

    return datafiles


def is_datafile_healthy(file_path):
    """
    Check that the data file does not contain empty dataset
    Parameters
    ----------
    file_path (str): the path to the file

    Returns
    -------
    A boolean
    """
    dataset_emptiness = []

    _, ext = os.path.splitext(file_path)
    if ext in ['.hdf5', '.h5']:
        with tables.File(file_path, 'r') as f:
            for n in f.walk_nodes():
                if isinstance(n, tables.Table):
                    dataset_emptiness.append(n.shape[0])
    return not np.any(np.array(dataset_emptiness) == 0)


def compute_total_parameter_number(net):
    """
    Compute the total number of parameters of a network
    Parameters
    ----------
    net (nn.Module): the network

    Returns
    -------
    int: the number of parameters
    """
    return sum(
        param.clone().cpu().data.view(-1).size(0)
        for name, param in net.named_parameters()
    )


@deprecated("20-08-2021",
            "the camera parameters are now loaded from the camera geometry, read from datafiles",
            "get_camera_layout_from_geom")
def load_camera_parameters(camera_type):
    """
    Load camera parameters : nbCol and injTable
    Parameters
    ----------
    datafiles (List) : files to load data from
    camera_type (str): the type of camera to load data for ; eg 'LST_LSTCam'

    Returns
    -------
    A dictionary
    """
    camera_parameters = {}
    if camera_type == 'LST':
        camera_type = 'LST_LSTCam'
    if camera_type in ['LST_LSTCam', 'MST_FlashCam', 'MST_NectarCam', 'CIFAR']:
        camera_parameters['layout'] = 'Hex'
    else:
        camera_parameters['layout'] = 'Square'
    camera_parameters_file = pkg_resources.resource_filename(__name__, 'data/camera_parameters.h5')
    with tables.File(camera_parameters_file, 'r') as hdf5_file:
        camera_parameters['nbRow'] = hdf5_file.root[camera_type]._v_attrs.nbRow
        camera_parameters['nbCol'] = hdf5_file.root[camera_type]._v_attrs.nbCol
        camera_parameters['injTable'] = hdf5_file.root[camera_type].injTable[()]
        camera_parameters['pixelsPosition'] = hdf5_file.root[camera_type].pixelsPosition[()]

    return camera_parameters


def dump_experiment_config(experiment):
    """
    Load experiment info from the settings file
    Parameters
    ----------
    experiment (Experiment): experiment

    Returns
    -------

    """
    exp_settings = collections.OrderedDict({'exp_name': experiment.experiment_name,
                                            'gammalearn': version.__version__,
                                            'dataset_class': format_name(experiment.dataset_class),
                                            'dataset_parameters': experiment.dataset_parameters,

                                            })
    exp_settings['network'] = {format_name(experiment.model_net): {k: format_name(v)
                                                                   for k, v in experiment.net_parameters_dic.items()}}
    if experiment.checkpoint_path is not None:
        exp_settings['resume_checkpoint'] = os.path.join(os.path.dirname(experiment.checkpoint_path).split('/')[-1],
                                                         os.path.basename(experiment.checkpoint_path))
    if experiment.info is not None:
        exp_settings['info'] = experiment.info
    if experiment.train:
        exp_settings['files_folders'] = experiment.train_folders
        exp_settings['num_epochs'] = experiment.max_epochs
        exp_settings['batch_size'] = experiment.batch_size
        if experiment.image_filter:
            exp_settings['image filters'] = {format_name(filter_func): filter_param
                                             for filter_func, filter_param
                                             in experiment.image_filter.items()}
        if experiment.event_filter:
            exp_settings['event filters'] = {format_name(filter_func): filter_param
                                             for filter_func, filter_param
                                             in experiment.event_filter.items()}
        if experiment.data_augment is not None:
            exp_settings['data_augmentation'] = {
                format_name(experiment.data_augment['function']): experiment.data_augment['kwargs']
            }
        exp_settings['losses'] = {
            k: {
                'loss': format_name(v['loss']),
                'weight': v['loss_weight']
            }
            for k, v in experiment.targets.items()
        }

        exp_settings['loss_function'] = format_name(experiment.compute_loss)
        exp_settings['optimizer'] = {key: format_name(value) for key, value in experiment.optimizer_dic.items()}
        exp_settings['optimizer_parameters'] = {opt: {key: format_name(value)
                                                      for key, value in param.items()}
                                                for opt, param in experiment.optimizer_parameters.items()}
        if experiment.lr_schedulers is not None:
            exp_settings['lr_schedulers'] = {format_name(handler): param
                                             for handler, param in experiment.lr_schedulers.items()}
    if experiment.test:
        if experiment.test_folders is not None:
            exp_settings['test_folders'] = experiment.test_folders
        if experiment.test_image_filter:
            exp_settings['test image filters'] = {format_name(filter_func): filter_param
                                                  for filter_func, filter_param
                                                  in experiment.test_image_filter.items()}
        if experiment.test_event_filter:
            exp_settings['test event filters'] = {format_name(filter_func): filter_param
                                                  for filter_func, filter_param
                                                  in experiment.test_event_filter.items()}

    experiment_path = experiment.main_directory + '/' + experiment.experiment_name + '/'
    settings_path = experiment_path + experiment.experiment_name + '_settings.json'
    with open(settings_path, 'w') as f:
        json.dump(exp_settings, f)


def format_name(name):
    name = format(name)
    name = name.replace('<', '').replace('>', '').replace('class ', '').replace("'", "").replace('function ', '')
    return name.split(' at ')[0]


def check_particle_mapping(particle_dict):
    assert len(particle_dict) == len(set(particle_dict.values())), 'Each mc particle type must have its own class'


def merge_list_of_dict(list_of_dict):
    merge_dict = {}
    for dictionary in list_of_dict:
        for k, v in dictionary.items():
            if k not in merge_dict:
                merge_dict[k] = [v]
            else:
                merge_dict[k].append(v)
    return merge_dict


###########
# Filters #
###########
##################################################################################################
# Event base filters

def energyband_filter(dataset, energy=None, filter_only_gammas=False):
    """
    Filter dataset on energy (in TeV).
    Parameters
    ----------
    dataset (Dataset): the dataset to filter
    energy (float): energy in TeV
    filter_only_gammas (bool)

    Returns
    -------
    (list of bool): the mask to filter the data
    """
    if dataset.simu:
        if energy is None:
            energy = [0, np.inf]
        en_min = energy[0]
        en_max = energy[1]
        energy_mask = (dataset.dl1_params['mc_energy'] > en_min) & (dataset.dl1_params['mc_energy'] < en_max)
        if filter_only_gammas:
            energy_mask = energy_mask | (dataset.dl1_params['mc_type'] != GAMMA_ID)
    else:
        energy_mask = np.full(len(dataset.dl1_params), True)
    return energy_mask


def telescope_multiplicity_filter(dataset, multiplicity, strict=False):
    """
    Filter dataset on number of telescopes that triggered (for a particular type of telescope)
    Parameters
    ----------
    dataset (Dataset): the dataset to filter
    multiplicity (int): the number of telescopes that triggered
    strict (bool)

    Returns
    -------
    (list of bool): the mask to filter the data
    """

    event_ids, mult = np.unique(dataset.dl1_params['event_id'], return_counts=True)
    event_id_mask = mult == multiplicity if strict else mult >= multiplicity

    return np.in1d(dataset.dl1_params['event_id'], event_ids[event_id_mask])


def emission_cone_filter(dataset, max_angle=np.inf):
    """
    Filter the dataset on the maximum distance between the impact point and the telescope position in km
    Parameters
    ----------
    dataset (Dataset): the dataset to filter
    max_angle (float): the max angle between the telescope pointing direction and the direction of the shower in rad

    Returns
    -------
    (list of bool): the mask to filter the data
    """
    if dataset.simu:
        separations = angular_separation_altaz(dataset.dl1_params['mc_alt'], dataset.dl1_params['mc_az'],
                                               dataset.dl1_params['mc_alt_tel'], dataset.dl1_params['mc_az_tel'])
        mask = separations <= max_angle
    else:
        mask = np.full(len(dataset.dl1_params), True)
    return mask


def impact_distance_filter(dataset, max_distance=np.inf):
    """
    Filter the dataset on the maximum distance between the impact point and the telescope position in km
    Parameters
    ----------
    dataset (Dataset): the dataset to filter
    max_distance (float): the maximum distance between the impact point and the telescope position in km

    Returns
    -------
    (list of bool): the mask to filter the data
        """
    if dataset.simu:
        distances = np.sqrt((dataset.dl1_params['mc_core_x'] - dataset.dl1_params['tel_pos_x']) ** 2 +
                            (dataset.dl1_params['mc_core_y'] - dataset.dl1_params['tel_pos_y']) ** 2)
        mask = distances < max_distance
    else:
        mask = np.full(len(dataset.dl1_params), True)
    return mask


##################################################################################################
# Image base filters

def intensity_filter(dataset, intensity=None, cleaning=False, dl1=False, **opts):
    """
    Filter dataset on intensity (in pe)
    Parameters
    ----------
    dataset (Dataset) : the dataset to filter
    a (int): total intensity in photoelectrons
    cleaning (bool): cut after cleaning
    dl1 (bool): whether to use the info computed by lstchain or to recompute the value
    opts (dict): cleaning options

    Returns
    -------
    (list of bool): the mask to filter the data
    """
    if intensity is None:
        intensity = [-np.inf, np.inf]
    pe_min = intensity[0]
    pe_max = intensity[1]

    if dl1:
        return (pe_min < dataset.dl1_params['intensity']) & (dataset.dl1_params['intensity'] < pe_max)
    else:

        def clean(img):
            mask = tailcuts_clean(geom, img, **opts)
            return img * mask

        if cleaning:
            geom = dataset.original_geometry
            image_cleaned = np.apply_along_axis(clean, 1, dataset.images)
            amps = image_cleaned.sum(axis=-1)
        else:
            amps = dataset.images.sum(axis=-1)
        mask1 = pe_min < amps
        mask2 = amps < pe_max
        mask = mask1 & mask2
        return mask


def cleaning_filter(dataset, dl1=False, **opts):
    """
    Filter images according to a cleaning operation.

    Parameters
    ----------
    dataset: `Dataset`
    dl1: (bool) whether to use the info computed by lstchain or to recompute the value

    Returns
    -------
    (list of bool): the mask to filter the data
    """
    if dl1:
        return dataset.dl1_params['n_pixels'] > 0
    else:
        geom = dataset.original_geometry

        def clean(img):
            return tailcuts_clean(geom, img, **opts)

        clean_mask = np.apply_along_axis(clean, 1, dataset.images)
        mask = clean_mask.any(axis=1)

        return mask


def leakage_filter(dataset, leakage1_cut=None, leakage2_cut=None, dl1=False, **opts):
    """
    Filter images according to a cleaning operation.

    Parameters
    ----------
    dataset: `Dataset`
    leakage1_cut: `int`
    leakage2_cut: `int`
    dl1: `bool` whether to use the info computed by lstchain or to recompute the value

    Returns
    -------
    (list of bool): the mask to filter the data
    """
    assert leakage1_cut is not None or leakage2_cut is not None, 'Leakage filter: At least one cut must be defined'
    if dl1:
        if leakage1_cut is not None:
            img_mask1 = dataset.dl1_params['leakage_intensity_width_1'] < leakage1_cut
        else:
            img_mask1 = np.full(len(dataset.dl1_params), True)

        if leakage2_cut is not None:
            img_mask2 = dataset.dl1_params['leakage_intensity_width_2'] < leakage2_cut
        else:
            img_mask2 = np.full(len(dataset.dl1_params), True)

        img_mask = img_mask1 & img_mask2

        return img_mask
    else:
        geom = dataset.original_geometry

        def leak2(img):
            mask = tailcuts_clean(geom, img, **opts)
            if np.any(mask):
                return leakage_parameters(geom, img, mask).intensity_width_2
            else:
                return 1.

        def leak1(img):
            mask = tailcuts_clean(geom, img, **opts)
            if np.any(mask):
                return leakage_parameters(geom, img, mask).intensity_width_1
            else:
                return 1.

        if leakage1_cut is not None:
            image_leak1 = np.apply_along_axis(leak1, 1, dataset.images)
            img_mask1 = image_leak1 < leakage1_cut
        else:
            img_mask1 = np.full(dataset.images.shape[0], True)

        if leakage2_cut is not None:
            image_leak2 = np.apply_along_axis(leak2, 1, dataset.images)
            img_mask2 = image_leak2 < leakage2_cut
        else:
            img_mask2 = np.full(dataset.images.shape[0], True)

        img_mask = img_mask1 & img_mask2

        return img_mask


def shower_position_filter(dataset, max_distance, dl1=False, **opts):
    """Filter images according to the position of the centroid of the shower.
    The image is cleaned then Hillas parameters are computed. For the LST a distance of 0.5 m corresponds to 10 pixels.

    Parameters
    ----------
    dataset (`Dataset`)
    max_distance (float): distance to the center of the camera in meters
    opts (dict): cleaning options
    dl1 (bool): whether to use the info computed by lstchain or to recompute the value

    Returns
    -------
    (list of bool): the mask to filter the data

    """
    if dl1:
        shower_distance = dataset.dl1_params['x']**2 + dataset.dl1_params['y']**2
        return shower_distance < max_distance ** 2
    else:
        geom = dataset.original_geometry

        def shower_centroid(img):
            mask = tailcuts_clean(geom, img, **opts)
            if np.any(mask):
                hillas = hillas_parameters(geom[mask], img[mask])
                return hillas.x.value ** 2 + hillas.y.value ** 2
            else:
                return np.inf

        shower_distance = np.apply_along_axis(shower_centroid, 1, dataset.images)
        img_mask = shower_distance < max_distance ** 2

        return img_mask


###################
# Transformations #
###################

def rotated_indices(pixels_position, theta):
    """
    Function that returns the rotated indices of an image from the pixels position.
    
    Parameters
    ----------
    pixels_position (numpy.Array): an array of shape (n, 2) of the position of the pixels
    theta (float): angle of rotation

    Returns
    -------
    Rotated indices
    """
    from math import isclose
    rot_indices = np.zeros(len(pixels_position)).astype(int)
    rotation_matrix = [[np.cos(theta), -np.sin(theta)],
                       [np.sin(theta), np.cos(theta)]]
    new_pix_pos = np.matmul(rotation_matrix, pixels_position.T).T.astype(np.float32)

    for i, pos in enumerate(new_pix_pos):
        for j, old_pos in enumerate(pixels_position):
            if isclose(old_pos[0], pos[0], abs_tol=10e-5) and isclose(old_pos[1], pos[1], abs_tol=10e-5):
                rot_indices[j] = i
    assert len(set(list(rot_indices))) == len(pixels_position), \
        'Rotated indices do not match the length of pixels position.'

    return rot_indices


# TODO move to transforms
def center_time(dataset, **opts):
    """
    Center pixel time based on the max intensity pixel

    Parameters
    ----------
    dataset: `Dataset`

    Returns
    -------
    indices: `numpy.array`
    """
    geom = dataset.camera_geometry

    def clean(img):
        return tailcuts_clean(geom, img, **opts)

    clean_mask = np.apply_along_axis(clean, 1, dataset.images)

    cleaned = dataset.images * clean_mask
    max_pix = cleaned.argmax(axis=1)
    for i, times in enumerate(dataset.times):
        times -= times[max_pix[i]]


# TODO move to transforms
def rgb_to_grays(dataset):
    """
    Function to convert RGB images to 2 channels gray images.
    Parameters
    ----------
    dataset (Dataset)
    """
    assert dataset.images.ndim in [3, 4]
    assert dataset.images.shape[1] == 3
    d_size = dataset.images.shape
    gamma = 2.2
    new_images = np.empty((d_size[0], 2) + d_size[2:], dtype=np.float32)
    new_images[:, 0:1] = np.sum(dataset.images, 1, keepdims=True)  # Naive sum
    new_images[:, 1:] = (0.2126 * dataset.images[:, 0:1]**gamma
                         + 0.7152 * dataset.images[:, 1:2]**gamma
                         + 0.0722 * dataset.images[:, 2:]**gamma)  # weighted sum

    dataset.images = new_images

    return np.arange(len(dataset))


def get_index_matrix_from_geom(camera_geometry):
    """
    Compute the index matrix from a ctapipe CameraGeometry

    Parameters
    ----------
    camera_geometry: `ctapipe.instrument.CameraGeometry`

    Returns
    -------
    indices_matrix: `numpy.ndarray`
        shape (n, n)

    """
    from ctapipe.image import geometry_converter_hex

    # the converter needs an image, let's create a fake one
    image = np.zeros(camera_geometry.n_pixels)

    # make sure the conversion matrix is recomputed
    if camera_geometry.camera_name in geometry_converter_hex.rot_buffer:
        del geometry_converter_hex.rot_buffer[camera_geometry.camera_name]

    geometry_converter_hex.convert_geometry_hex1d_to_rect2d(camera_geometry,
                                                            image,
                                                            key=camera_geometry.camera_name)

    hex_to_rect_map = geometry_converter_hex.rot_buffer[camera_geometry.camera_name][2]

    return np.flip(hex_to_rect_map, axis=0).astype(np.float32)


def get_camera_layout_from_geom(camera_geometry):
    """
    From a ctapipe camera geometry, compute the index matrix and the camera layout (`Hex` or `Square`) for indexed conv

    Parameters
    ----------
    camera_geometry: `ctapipe.instrument.CameraGeometry`

    Returns
    -------
    tensor_matrix: `torch.Tensor`
        shape (1, 1, n, n)
    camera_layout: `str`
        `Hex` or `Square`

    """
    index_matrix = get_index_matrix_from_geom(camera_geometry)
    tensor_matrix = torch.tensor(np.ascontiguousarray(index_matrix.reshape(1, 1, *index_matrix.shape)))
    if camera_geometry.pix_type.value == 'hexagon':
        camera_layout = 'Hex'
    elif camera_geometry.pix_type.value == 'square':
        camera_layout = 'Square'
    else:
        raise ValueError("Unkown camera pixels type")
    return tensor_matrix, camera_layout


def get_dataset_geom(d, geometries):
    """
    Update `geometries` by append the geometries from d

    Parameters
    ----------
    d: list or `torch.utils.ConcatDataset` or `torch.utils.data.Subset` or `torch.utils.data.Dataset`
    geometries: list

    """
    if isinstance(d, list):
        print('d is a list')
        for d_l in d:
            get_dataset_geom(d_l, geometries)
    elif isinstance(d, torch.utils.data.ConcatDataset):
        for d_c in d.datasets:
            get_dataset_geom(d_c, geometries)
    elif isinstance(d, torch.utils.data.Subset):
        get_dataset_geom(d.dataset, geometries)
    elif isinstance(d, torch.utils.data.Dataset):
        geometries.append(d.camera_geometry)


def nets_definition_path():
    """
    Return the path to the net definition file

    Returns
    -------
    str
    """
    return pkg_resources.resource_filename('gammalearn', 'data/nets.py')

