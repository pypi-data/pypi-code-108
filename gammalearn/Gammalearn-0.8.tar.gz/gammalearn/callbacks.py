import logging
import os
import pkg_resources

import torch
import torch.nn as nn
from torch.utils.data import Subset
from pytorch_lightning.callbacks import Callback
import numpy as np
import pandas as pd
import tables
from ctapipe.instrument import CameraGeometry
from ctapipe.visualization import CameraDisplay
from ctapipe.io import HDF5TableWriter
from lstchain.io import write_dl2_dataframe
from lstchain.reco.utils import add_delta_t_key
from PIL import Image
from torchvision import transforms
import torchvision.utils as t_utils
from indexedconv.engine import IndexedConv
from indexedconv.utils import create_index_matrix, img2mat, pool_index_matrix, build_hexagonal_position
from astropy.table import Table

import gammalearn.utils as utils
import gammalearn.criterions as criterions
import gammalearn.datasets as dsets
import gammalearn.version as gl_version
import gammalearn.constants as csts

from tables.scripts.ptrepack import copy_leaf

import matplotlib.pyplot as plt


class RunConfigDescription(tables.IsDescription):
    num_showers = tables.Int32Col()
    shower_reuse = tables.Int32Col()
    spectral_index = tables.Float64Col()
    max_scatter_range = tables.Float64Col()
    energy_range_max = tables.Float64Col()
    energy_range_min = tables.Float64Col()
    min_alt = tables.Float64Col()
    max_alt = tables.Float64Col()


class LogUncertaintyLogVars(Callback):
    """
    Callback to send loss log vars of the Uncertainty estimation method to logger
    Parameters
    ----------
    Returns
    -------
    """
    def on_train_epoch_end(self, trainer, pl_module):
        if isinstance(pl_module.experiment.compute_loss, criterions.MultilossBalancing):
            log_vars = pl_module.experiment.compute_loss.log_vars
            vars_dict = {}
            for i, task in enumerate(pl_module.experiment.targets.keys()):
                vars_dict['Logvar_' + task] = log_vars[i].detach().cpu()
            pl_module.log('Log_vars', vars_dict, on_epoch=True, on_step=False)


class LogGradNormWeights(Callback):
    """
    Callback to send GradNorm weights to logger
    Parameters
    ----------
    Returns
    -------
    """
    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        if isinstance(pl_module.experiment.compute_loss, criterions.GradNormBalancing):
            if pl_module.global_step % pl_module.experiment.save_every == 0:
                weights = pl_module.experiment.compute_loss.weights
                weights_dict = {}
                for i, task in enumerate(pl_module.experiment.targets.keys()):
                    weights_dict['Gradnorm_w_' + task] = weights[i]
                pl_module.log('Gradnorm_weights', weights_dict, on_step=True, on_epoch=False)


class LogModelWeightNorm(Callback):
    """
    Callback to send sum of squared weigths of the network to logger
    Parameters
    ----------
    Returns
    -------

    """
    def on_train_epoch_end(self, trainer, pl_module):
        weights = 0
        for name, param in pl_module.net.named_parameters():
            if 'weight' in name:
                weights += torch.sum(param.data ** 2)
        pl_module.log('weights', weights, on_epoch=True, on_step=False)


class LogModelParameters(Callback):
    """
    Callback to send the network parameters to logger
    Parameters
    ----------
    Returns
    -------
    """

    def on_train_epoch_end(self, trainer, pl_module):
        for name, param in pl_module.net.named_parameters():
            pl_module.logger.experiment.add_histogram(name, param.detach().cpu(),
                                                      bins='tensorflow',
                                                      global_step=pl_module.current_epoch)


def make_activation_sender(pl_module, name):
    """
    Creates the adapted activations sender to tensorboard
    Parameters
    ----------
    pl_module (LightningModule): the tensorboardX writer
    name (string) : name of the layer which activation is logged

    Returns
    -------
    An adapted function
    """

    def send(m, input, output):
        """
        The function to send the activation of a module to tensorboard
        Parameters
        ----------
        m (nn.Module): the module (eg nn.ReLU, ...)
        input
        output

        Returns
        -------

        """
        pl_module.logger.experiment.add_histogram(name, output.detach().cpu(),
                                                  bins='tensorflow', global_step=pl_module.current_epoch)

    return send


class LogReLUActivations(Callback):
    """
    Callback to send activations to logger
    Parameters
    ----------
    Returns
    -------
    """
    def setup(self, trainer, pl_module, stage):
        self.hooks = []

    def on_train_epoch_start(self, trainer, pl_module):
        for name, child in pl_module.net.named_children():
            if isinstance(child, nn.ReLU):
                sender = make_activation_sender(pl_module, name)
                self.hooks.append(child.register_forward_hook(sender))

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        for hook in self.hooks:
            hook.remove()


def make_linear_gradient_logger(pl_module, name):
    def log_grad(m, grad_input, grad_output):
        pl_module.logger.experiment.add_histogram(name + 'grad_in', grad_input[0].data.cpu(),
                                                  bins='tensorflow', global_step=pl_module.current_epoch)
    return log_grad


class LogLinearGradient(Callback):
    """
    Callback to send gradients to logger
    Parameters
    ----------
    Returns
    -------
    """

    def setup(self, trainer, pl_module, stage):
        self.hooks = []

    def on_train_epoch_start(self, trainer, pl_module):
        for name, child in pl_module.net.named_modules():
            if isinstance(child, nn.Linear):
                grad_logger = make_linear_gradient_logger(pl_module, name)
                self.hooks.append(child.register_full_backward_hook(grad_logger))

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        for hook in self.hooks:
            hook.remove()


def make_feature_logger(pl_module, name, index_matrices):
    def log_features(m, input, output):
        if output.dim() == 3:
            features = output.detach().cpu().clone()
            images_list = []
            index_matrix = index_matrices[features.shape[-1]]
            pixel_pos = np.array(build_hexagonal_position(index_matrix.squeeze().squeeze()))
            pix_area = np.full(features.shape[-1], 6/np.sqrt(3)*0.5**2)
            # TODO load meta from datafile
            geom = CameraGeometry.from_table(
                Table(
                    {
                        'pix_id': np.arange(features.shape[-1]),
                        'pix_x': list(map(lambda x: x[0], pixel_pos)),
                        'pix_y': list(map(lambda x: x[1], pixel_pos)),
                        'pix_area': pix_area,
                    },
                    meta={
                        'PIX_TYPE': 'hexagonal',
                        'PIX_ROT': 0,
                        'CAM_ROT': 0,
                    }
                )
            )

            for b, batch in enumerate(features):
                for c, channel in enumerate(batch):
                    label = '{}_b{}_c{}'.format(name, b, c)
                    ax = plt.axes(label=label)
                    ax.set_aspect('equal', 'datalim')
                    disp = CameraDisplay(geom, ax=ax)
                    disp.image = channel
                    disp.add_colorbar()
                    ax.set_title(label)
                    canvas = plt.get_current_fig_manager().canvas
                    canvas.draw()
                    pil_img = Image.frombytes('RGB', canvas.get_width_height(), canvas.tostring_rgb())
                    images_list.append(transforms.ToTensor()(pil_img))

            grid = t_utils.make_grid(images_list)

            pl_module.logger.experiment.add_image('Features_{}'.format(name),
                                                  grid, pl_module.current_epoch)
    return log_features


class LogFeatures(Callback):

    def setup(self, trainer, pl_module, stage):
        self.hooks = []
        self.index_matrices = {}
        index_matrix = create_index_matrix(pl_module.camera_parameters['nbRow'],
                                           pl_module.camera_parameters['nbCol'],
                                           pl_module.camera_parameters['injTable'])
        n_pixels = int(torch.sum(torch.ge(index_matrix[0, 0], 0)).data)
        self.index_matrices[n_pixels] = index_matrix
        idx_matx = index_matrix
        while n_pixels > 1:
            idx_matx = pool_index_matrix(idx_matx, kernel_type=pl_module.camera_parameters['layout'])
            n_pixels = int(torch.sum(torch.ge(idx_matx[0, 0], 0)).data)
            self.index_matrices[n_pixels] = idx_matx

    def on_train_epoch_start(self, trainer, pl_module):
        for name, child in pl_module.net.named_children():
            if isinstance(child, nn.ReLU):
                feature_logger = make_feature_logger(pl_module, name, self.index_matrices)
                self.hooks.append(child.register_forward_hook(feature_logger))

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        for hook in self.hooks:
            hook.remove()


# def create_send_kernels_to_tensorboard(experiment):
#     """
#
#     Parameters
#     ----------
#     experiment
#
#     Returns
#     -------
#
#     """
#     logger = logging.getLogger(__name__)
#     if net.conv_kernel == 'Pool':
#         kernel = np.ones((2, 2), dtype=bool)
#     elif net.conv_kernel == 'Hex_2':
#         kernel = np.ones((5, 5), dtype=bool)
#         kernel[0, 3:5] = False
#         kernel[1, 4] = False
#         kernel[3:5, 0] = False
#         kernel[4, 1] = False
#
#     else:
#         kernel = np.ones((3, 3), dtype=bool)
#         if net.conv_kernel == 'Hex':
#             kernel[0, 2] = False
#             kernel[2, 0] = False
#     idx = 0
#     index_matrix = np.ones(kernel.shape) * -1
#     for i in range(kernel.shape[0]):
#         for j in range(kernel.shape[1]):
#             if kernel[i, j]:
#                 index_matrix[i, j] = idx
#                 idx += 1
#     # TODO check if it still works
#     camera_type = experiment.dataset_parameters['camera_type']
#     camera_type = 'LST_LSTCam' if camera_type == 'LST' else camera_type
#     geom = CameraGeometry.from_name(camera_type.split('_')[1])  # camera_type is of form LST_LSTCam
#
#     def send_kernels(engine):
#
#         epoch = engine.state.epoch
#         ax = plt.axes()
#         ax.set_aspect('equal', 'datalim')
#         for name, child in net.named_children():
#             logger.debug(name)
#             if isinstance(child, IndexedConv):
#                 for name_p, parameter in child.named_parameters():
#                     if name_p == 'weight':
#                         conv_weight = parameter
#                 images_list = []
#                 for i in range(conv_weight.shape[0]):
#                     kernel_vec = torch.sum(conv_weight[i], 0)  # TODO plot the kernel with max total value
#                     logger.debug('kernel {} shape {}'.format(i, kernel_vec.shape))
#                     ax.clear()
#                     disp = CameraDisplay(geom)
#                     disp.image = kernel_vec.detach()
#                     canvas = plt.get_current_fig_manager().canvas
#                     canvas.draw()
#                     pil_img = Image.frombytes('RGB', canvas.get_width_height(), canvas.tostring_rgb())
#                     images_list.append(transforms.ToTensor()(pil_img))
#
#                 grid = t_utils.make_grid(images_list)
#
#                 experiment.tensorboard_writer.add_image('Kernel_{}'.format(name), grid, epoch)
#
#     return send_kernels


class LogGradientNorm(Callback):
    """
    Callback to send the gradient total norm to logger
    Parameters
    ----------
    Returns
    -------
    """
    def on_train_epoch_end(self, trainer, pl_module):
        pl_module.log('Gradient_norm', pl_module.grad_norm, on_epoch=True, on_step=False)



# TODO create a scheduler like class for the regulariztion coefficient
# def create_regularization_multistep_handler(experiment, **options):
#     """
#     Handler to update the regularization coefficient
#     Parameters
#     ----------
#     experiment (Experiment):
#
#     Returns
#     -------
#     A function registrable by ignite Trainer
#     """
#     logger = logging.getLogger(__name__)
#     if options is not None:
#         try:
#             milestones = options['milestones']
#         except (TypeError, KeyError) as e:
#             logger.warning('MultiStep regularization needs a list of milestones. Setting default value to [20, 50, 70]')
#             logger.error(e)
#             milestones = [20, 50, 70]
#         try:
#             coefficient = options['lambda']
#         except (TypeError, KeyError) as e:
#             logger.warning('MultiStep regularization needs the list of coefficient. Setting default value to '
#                            '[1e-3, 1e-4, 1e-6]')
#             logger.error(e)
#             coefficient = [1e-3, 1e-4, 1e-6]
#
#     def update_regularization(engine):
#         if engine.state.trainer_epoch == milestones[0]:
#             experiment.regularization['weight'] = coefficient[0]
#             milestones.pop(0)
#             coefficient.pop(0)
#
#     return update_regularization


class WriteDL2Files(Callback):
    """
        Callback to produce testing result data files
        Parameters
        ----------
        trainer (Trainer)
        pl_module (LightningModule)

        Returns
        -------
        """
    def on_test_end(self, trainer, pl_module):

        # Retrieve test data
        merged_outputs = utils.merge_list_of_dict(pl_module.test_data['output'])
        merged_dl1_params = utils.merge_list_of_dict(pl_module.test_data['dl1_params'])

        for k, v in merged_outputs.items():
            merged_outputs[k] = torch.cat(v).detach().to('cpu').numpy()
        for k, v in merged_dl1_params.items():
            merged_dl1_params[k] = torch.cat(v).detach().to('cpu').numpy()

        particle_dict = pl_module.experiment.dataset_parameters['particle_dict']
        swapped_particle_dict = {v: k for k, v in particle_dict.items()}

        # Prepare data
        data_pd = pd.DataFrame()
        for param_name, param_value in merged_dl1_params.items():
            if param_name in ['mc_core_x', 'mc_core_y', 'tel_pos_x', 'tel_pos_y', 'tel_pos_z', 'mc_x_max']:
                data_pd[param_name] = 1000 * param_value
            else:
                data_pd[param_name] = param_value
        for target, output in merged_outputs.items():
            if target == 'energy':
                data_pd['reco_energy'] = 10 ** output
            if target == 'xmax':
                data_pd['reco_x_max'] = output * 1000
            if target == 'impact':
                data_pd['reco_core_x'] = output[:, 0] * 1000
                data_pd['reco_core_y'] = output[:, 1] * 1000
                if pl_module.experiment.dataset_parameters['group_by'] == 'image':
                    data_pd['reco_core_x'] += data_pd['tel_pos_x']
                    data_pd['reco_core_y'] += data_pd['tel_pos_y']
            if target == 'direction':
                data_pd['reco_alt'] = output[:, 0]
                data_pd['reco_az'] = output[:, 1]
                if pl_module.experiment.dataset_parameters['group_by'] == 'image':
                    alt_tel = data_pd['mc_alt_tel'] if 'mc_alt_tel' in data_pd else data_pd['alt_tel']
                    az_tel = data_pd['mc_az_tel'] if 'mc_az_tel' in data_pd else data_pd['az_tel']
                    data_pd['reco_alt'] += alt_tel
                    data_pd['reco_az'] += az_tel
            if target == 'class':
                data_pd['reco_particle'] = np.vectorize(swapped_particle_dict.get)(np.argmax(output, 1))
                data_pd['gammaness'] = np.exp(output[:, particle_dict[csts.GAMMA_ID]])
                for k, v in particle_dict.items():
                    data_pd['reco_proba_{}'.format(k)] = np.exp(output[:, v])

        if pl_module.experiment.test_folders is None:
            # Test has be done on the validation set
            # Retrieve MC config information
            mc_configuration = {}

            def fetch_dataset_info(d):
                if isinstance(d, torch.utils.data.ConcatDataset):
                    for d_c in d.datasets:
                        fetch_dataset_info(d_c)
                elif isinstance(d, Subset):
                    fetch_dataset_info(d.dataset)
                elif issubclass(pl_module.experiment.dataset_class, dsets.BaseLSTDataset):
                    particle_type = d.dl1_params['mc_type'][0]
                    if particle_type not in mc_configuration:
                        mc_configuration[particle_type] = {'mc_energies': [], 'run_configs': []}
                    if d.simu:
                        mc_energies = d.trig_energies
                        if not pl_module.experiment.split_by_file and pl_module.experiment.test_folders is None:
                            np.random.shuffle(mc_energies)
                            mc_energies = mc_energies[:int(len(mc_energies) * pl_module.experiment.validating_ratio)]
                            d.run_config['mcheader']['num_showers'] *= pl_module.experiment.validating_ratio
                        mc_configuration[particle_type]['mc_energies'].extend(mc_energies)
                    mc_configuration[particle_type]['run_configs'].append(d.run_config)
                else:
                    pl_module.console_logger.error('Unknown dataset type, MC configuration cannot be retrieved')
                    raise ValueError

            for dataloader in trainer.test_dataloaders:
                fetch_dataset_info(dataloader.dataset)

            # Write one file per particle type
            for mc_type in mc_configuration:
                particle_mask = data_pd['mc_type'] == mc_type

                gb_file_path = pl_module.experiment.main_directory + '/' + pl_module.experiment.experiment_name + '/' + \
                               pl_module.experiment.experiment_name + '_' + str(mc_type) + '.h5'
                if os.path.exists(gb_file_path):
                    os.remove(gb_file_path)

                writer = HDF5TableWriter(gb_file_path)
                dl1_version = []
                ctapipe_version = []
                runlist = []

                for config in mc_configuration[mc_type]['run_configs']:
                    try:
                        dl1_version.append(config['metadata']['LSTCHAIN_VERSION'])
                    except Exception:
                        pl_module.console_logger.warning('There is no LSTCHAIN_VERSION in run config')
                    try:
                        ctapipe_version.append(config['metadata']['CTAPIPE_VERSION'])
                    except Exception:
                        pl_module.console_logger.warning('There is no CTAPIPE_VERSION in run config')
                    try:
                        runlist.extend(config['metadata']['SOURCE_FILENAMES'])
                    except Exception:
                        pl_module.console_logger.warning('There is no SOURCE_FILENAMES in run config')
                    try:
                        writer.write('simulation/run_config', config['mcheader'])
                    except Exception:
                        pl_module.console_logger.warning('Issue when writing run config')
                writer.close()

                try:
                    assert len(set(dl1_version)) == 1
                except AssertionError:
                    warning_msg = 'There should be strictly one dl1 data handler version in dataset but there are {}'.format(set(dl1_version))
                    pl_module.console_logger.warning(warning_msg)
                    dl1_version = 'Unknown'
                else:
                    dl1_version = dl1_version[0]

                try:
                    assert len(set(ctapipe_version)) == 1
                except AssertionError:
                    warning_msg = 'There should be strictly one ctapipe version in dataset but there are {}'.format(set(ctapipe_version))
                    pl_module.console_logger.warning(warning_msg)
                    ctapipe_version = 'Unknown'
                else:
                    ctapipe_version = ctapipe_version[0]

                try:
                    assert runlist
                except AssertionError:
                    pl_module.console_logger.warning('Run list is empty')

                metadata = {
                    'LSTCHAIN_VERSION': dl1_version,
                    'CTAPIPE_VERSION': ctapipe_version,
                    'mc_type': mc_type,
                    'GAMMALEARN_VERSION': gl_version.__version__,
                }

                with tables.open_file(gb_file_path, mode='a') as file:
                    for k, item in metadata.items():
                        if k in file.root._v_attrs and type(file.root._v_attrs) is list:
                            attribute = file.root._v_attrs[k].extend(metadata[k])
                            file.root._v_attrs[k] = attribute
                        else:
                            file.root._v_attrs[k] = metadata[k]
                    if runlist and '/simulation' in file:
                        file.create_array('/simulation', 'runlist', obj=runlist)

                pd.DataFrame(
                    {
                        'mc_trig_energies': np.array(mc_configuration[mc_type]['mc_energies'])
                    }
                ).to_hdf(gb_file_path,
                         key='triggered_events')

                data_pd[particle_mask].to_hdf(gb_file_path, key='data')
        else:
            # Prepare output
            if pl_module.experiment.dl2_path is not None:
                output_dir = pl_module.experiment.dl2_path
            else:
                output_dir = pl_module.experiment.main_directory + '/' + pl_module.experiment.experiment_name + '/dl2/'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            dataset = trainer.test_dataloaders[0].dataset
            output_name = os.path.basename(dataset.hdf5_file_path)
            output_name = output_name.replace('dl1', 'dl2')
            output_path = os.path.join(output_dir, output_name)
            if os.path.exists(output_path):
                os.remove(output_path)

            mc_type = dataset.dl1_params['mc_type'][0]
            mc_energies = dataset.trig_energies

            metadata = dataset.run_config['metadata']
            metadata['mc_type'] = mc_type
            metadata['GAMMALEARN_VERSION'] = gl_version.__version__
            # Copy dl1 info except images
            with tables.open_file(dataset.hdf5_file_path) as dl1:
                for node in dl1.walk_nodes():
                    if not isinstance(node, tables.group.Group) and 'image' not in node._v_pathname:
                        stats = {'groups': 0, 'leaves': 0, 'links': 0, 'bytes': 0, 'hardlinks': 0}
                        copy_leaf(
                            dataset.hdf5_file_path, output_path, node._v_pathname, node._v_pathname,
                            title='', filters=None,
                            copyuserattrs=True,
                            overwritefile=False, overwrtnodes=True,
                            stats=stats, start=None, stop=None, step=1,
                            chunkshape='keep',
                            sortby=None, check_CSI=False,
                            propindexes=False,
                            upgradeflavors=False,
                            allow_padding=True,
                        )
            # Write dl2 info
            if not dataset.simu:
                # Post dl2 ops for real data
                data_pd = add_delta_t_key(data_pd)
            write_dl2_dataframe(data_pd, output_path)
            # Write metadata
            if mc_energies is not None:
                pd.DataFrame({'mc_trig_energies': np.array(mc_energies)}).to_hdf(output_path, key='triggered_events')
            with tables.open_file(output_path, mode='a') as file:
                for k, item in metadata.items():
                    if k in file.root._v_attrs and type(file.root._v_attrs) is list:
                        attribute = file.root._v_attrs[k].extend(metadata[k])
                        file.root._v_attrs[k] = attribute
                    else:
                        file.root._v_attrs[k] = metadata[k]


class WriteAEOutput(Callback):
    """
        Callback to produce testing result data files
        Parameters
        ----------
        trainer (Trainer)
        pl_module (LightningModule)

        Returns
        -------
        """
    def on_test_end(self, trainer, pl_module):

        # Retrieve test data
        merged_outputs = utils.merge_list_of_dict(pl_module.test_data['output'])
        merged_dl1_params = utils.merge_list_of_dict(pl_module.test_data['dl1_params'])

        for k, v in merged_outputs.items():
            merged_outputs[k] = torch.cat(v).detach().to('cpu').numpy()
        for k, v in merged_dl1_params.items():
            merged_dl1_params[k] = torch.cat(v).detach().to('cpu').numpy()

        # Prepare data
        data_pd = pd.DataFrame()
        for param_name, param_value in merged_dl1_params.items():
            if param_name in ['mc_core_x', 'mc_core_y', 'tel_pos_x', 'tel_pos_y', 'tel_pos_z', 'mc_x_max']:
                data_pd[param_name] = 1000 * param_value
            else:
                data_pd[param_name] = param_value
        for target, output in merged_outputs.items():
            data_pd[target] = output

        if pl_module.experiment.test_folders is None:
            # Test has be done on the validation set
            # Write one file
            output_path = os.path.join(pl_module.experiment.main_directory, pl_module.experiment.experiment_name,
                                       pl_module.experiment.experiment_name + '_ae_validation_results.h5')
            if os.path.exists(output_path):
                os.remove(output_path)
        else:
            # One output file per dl1 file
            # Prepare output
            output_dir = os.path.join(pl_module.experiment.main_directory,
                                      pl_module.experiment.experiment_name,
                                      'ae_test_results')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            dataset = trainer.test_dataloaders[0].dataset
            output_name = os.path.basename(dataset.hdf5_file_path)
            output_name = output_name.replace('dl1', 'ae_results')
            output_path = os.path.join(output_dir, output_name)
            if os.path.exists(output_path):
                os.remove(output_path)
        data_pd.to_hdf(output_path, key='data')
