#!/usr/bin/env python

from __future__ import division, print_function
import os
import argparse
import importlib.util
import inspect
import logging
import shutil
import faulthandler

import torch
import torch.backends.cudnn as cudnn

from pytorch_lightning import LightningModule
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning.callbacks import ModelCheckpoint, DeviceStatsMonitor, LearningRateMonitor
import pytorch_lightning as pl

from gammalearn.version import __version__ as _version
from gammalearn.utils import (check_particle_mapping, compute_total_parameter_number, get_dataset_geom,
                              prepare_experiment_folder, dump_experiment_config)
from gammalearn.data_handlers import GLearnDataModule
from gammalearn.datasets import WrongGeometryError

from gammalearn.logging import LOGGING_CONFIG

faulthandler.enable()


class Experiment(object):
    """Loads the settings of the experiment from the settings object,
    check them and defines default values for not specified ones.
    """

    def __init__(self, settings):
        """
        Parameters
        ----------
        settings : the object created from the settings.py import
        """
        self._logger = logging.getLogger(__name__)
        self.hooks = {}
        self.camera_geometry = None

        ##################################################################################################
        # Experiment settings

        self._settings = settings
        # Load mandatory settings
        # Experiment settings
        self._has_mandatory('main_directory', 'where the experiments are stored')
        self.main_directory = settings.main_directory

        self._has_mandatory('experiment_name', 'the name of the experiment !')
        self.experiment_name = settings.experiment_name

        self._has_mandatory(
            'gpus', 'the gpus to use. If -1, run on all GPUS, if None/0 run on CPU. If list, run on GPUS of list.')
        assert isinstance(getattr(settings, 'gpus'), (int, list)) or getattr(settings, 'gpus') is None, \
            'CUDA device id must be int, list of int or None !'
        if not torch.cuda.is_available() and settings.gpus not in [None, 0]:
            self._logger.warning('Experiment requested to run on GPU, but GPU not available. Run on CPU')
            self.gpus = None
        else:
            self.gpus = settings.gpus
        self.ddp = 'ddp' if self.gpus not in [0, None] else None

        self._has_mandatory('dataset_class', 'the class to load the data')
        self.dataset_class = settings.dataset_class

        self._has_mandatory('dataset_parameters', 'the parameters of the dataset (camera type, group by option...)')
        self.dataset_parameters = settings.dataset_parameters
        check_particle_mapping(self.dataset_parameters['particle_dict'])

        self._has_mandatory('targets', 'the targets to reconstruct')
        self.targets = settings.targets
        if 'class' in self.targets:
            try:
                assert 'output_shape' not in self.targets['class']
            except AssertionError:
                self._logger.warning('Output shape of target class defined in settings will be overwritten with '
                                     'particle_dict length')
            self.targets['class']['output_shape'] = len(self.dataset_parameters['particle_dict'])

        # Net settings
        self._has_mandatory('net_definition_file', 'the file containing the net class')
        self.net_definition_file = settings.net_definition_file

        self._has_mandatory('model_net', 'the net to use')
        self.model_net = settings.model_net

        self._has_mandatory('net_parameters_dic', 'the parameters of the net described by a dictionary')
        assert isinstance(getattr(settings, 'net_parameters_dic'), dict), 'The net parameters must be a dict !'
        self.net_parameters_dic = settings.net_parameters_dic
        self.net_parameters_dic['targets'] = {k: v['output_shape'] for k, v in self.targets.items()}

        self._has_mandatory('train', 'whether to test the model after training')
        self._is_of_type('train', bool)
        self.train = settings.train

        self._has_mandatory('test', 'whether to test the model after training')
        self._is_of_type('test', bool)
        self.test = settings.test

        # Optional experiments settings
        if hasattr(settings, 'info'):
            self._is_of_type('info', str)
            self.info = settings.info
        else:
            self.info = None

        if hasattr(settings, 'log_every_n_steps'):
            self._is_positive('log_every_n_steps')
            self.log_every_n_steps = settings.log_every_n_steps
        else:
            self.log_every_n_steps = 100

        if hasattr(settings, 'save_every'):
            self._is_of_type('save_every', int)
            self.save_every = max(settings.save_every, 0)
        else:
            self.save_every = None

        if hasattr(settings, 'random_seed'):
            self._is_of_type('random_seed', int)
            self.random_seed = settings.random_seed
        else:
            self.random_seed = None

        if hasattr(settings, 'monitor_gpus'):
            self._is_of_type('monitor_gpus', bool)
            self.monitor_gpus = settings.monitor_gpus
        else:
            self.monitor_gpus = False

        if hasattr(settings, 'data_transform'):
            self._is_of_type('data_transform', dict)
            self.data_transform = settings.data_transform
        else:
            self.data_transform = None

        if hasattr(settings, 'preprocessing_workers'):
            self._is_of_type('preprocessing_workers', int)
            self.preprocessing_workers = max(settings.preprocessing_workers, 0)
        else:
            self.preprocessing_workers = 0

        if hasattr(settings, 'dataloader_workers'):
            self._is_of_type('dataloader_workers', int)
            self.dataloader_workers = max(settings.dataloader_workers, 0)
        else:
            self.dataloader_workers = 0

        if hasattr(settings, 'mp_start_method'):
            self._is_of_type('mp_start_method', str)
            try:
                assert settings.mp_start_method in ['fork', 'spawn']
            except AssertionError:
                self.mp_start_method = torch.multiprocessing.get_start_method()
            else:
                self.mp_start_method = settings.mp_start_method
        else:
            self.mp_start_method = torch.multiprocessing.get_start_method()

        if hasattr(settings, 'checkpoint_path'):
            self.checkpoint_path = settings.checkpoint_path
        else:
            self.checkpoint_path = None

        self.profiler = settings.profiler if hasattr(settings, 'profiler') else None

        #################################################################################################
        # Train settings
        if self.train:
            # Data settings
            self._has_mandatory('train_folders', 'the training and validating data folders')
            self.train_folders = settings.train_folders

            self._has_mandatory('validating_ratio', 'the ratio of data for validation')
            self.validating_ratio = settings.validating_ratio

            self._has_mandatory('max_epochs', 'the maximum number of epochs')
            self.max_epochs = settings.max_epochs

            self._has_mandatory('batch_size', 'the batch size')
            self._is_positive('batch_size')
            self.batch_size = settings.batch_size

            # Training settings
            self._has_mandatory('compute_loss', 'the function to compute the loss')
            self.compute_loss = settings.compute_loss

            self._has_mandatory('optimizer_parameters', 'the optimizers parameters described as a dictionary')
            self.optimizer_parameters = settings.optimizer_parameters

            self._has_mandatory('optimizer_dic', 'the optimizers described as a dictionary')
            self.optimizer_dic = settings.optimizer_dic

            self._has_mandatory('training_step', 'the function for the training step')
            self._is_function('training_step', 2)
            self.training_step = settings.training_step

            self._has_mandatory('eval_step', 'the function for the evaluation step')
            self._is_function('eval_step', 2)
            self.eval_step = settings.eval_step

            # Optional settings
            if hasattr(settings, 'image_filter'):
                self._is_of_type('image_filter', dict)
                self.image_filter = settings.image_filter
            else:
                self.image_filter = {}

            if hasattr(settings, 'event_filter'):
                self._is_of_type('event_filter', dict)
                self.event_filter = settings.event_filter
            else:
                self.event_filter = {}
            if hasattr(settings, 'data_augment'):
                self._is_of_type('data_augment', dict)
                self.data_augment = settings.data_augment
            else:
                self.data_augment = None

            if hasattr(settings, 'dataset_size'):
                self._is_of_type('dataset_size', int)
                self.dataset_size = settings.dataset_size
            else:
                self.dataset_size = None

            if hasattr(settings, 'files_max_number'):
                self._is_of_type('files_max_number', int)
                self.files_max_number = settings.files_max_number
            else:
                self.files_max_number = None

            if hasattr(settings, 'pin_memory'):
                self._is_of_type('pin_memory', bool)
                self.pin_memory = settings.pin_memory
            else:
                self.pin_memory = False

            if hasattr(settings, 'split_by_file'):
                self._is_of_type('split_by_file', bool)
                self.split_by_file = settings.split_by_file
            else:
                self.split_by_file = True

            if hasattr(settings, 'regularization'):
                self.regularization = settings.regularization
            else:
                self.regularization = None

            if hasattr(settings, 'check_val_every_n_epoch'):
                self._is_positive('check_val_every_n_epoch')
                self.check_val_every_n_epoch = settings.check_val_every_n_epoch
            else:
                self.check_val_every_n_epoch = 1

            if hasattr(settings, 'lr_schedulers'):
                self.lr_schedulers = settings.lr_schedulers
            else:
                self.lr_schedulers = None

            if hasattr(settings, 'training_callbacks'):
                self.training_callbacks = settings.training_callbacks
            else:
                self.training_callbacks = []

        else:
            self.train_folders = None
            self.validating_ratio = None
            self.max_epochs = 0
            self.batch_size = None
            self.compute_loss = None
            self.optimizer_parameters = None
            self.optimizer_dic = None
            self.training_step = None
            self.eval_step = None
            self.image_filter = {}
            self.event_filter = {}
            self.data_augment = None
            self.dataset_size = None
            self.files_max_number = None
            self.pin_memory = False
            self.split_by_file = True
            self.regularization = None
            self.check_val_every_n_epoch = 1
            self.lr_schedulers = None
            self.training_callbacks = []

        ########################################################################################################
        # Test settings
        if self.test:
            self._has_mandatory('test_step', 'the test iteration')
            self._is_function('test_step', 2)
            self.test_step = settings.test_step

            if hasattr(settings, 'test_dataset_parameters'):
                self._is_of_type('test_dataset_parameters', dict)
                self.test_dataset_parameters = settings.test_dataset_parameters
            else:
                self.test_dataset_parameters = None

            if hasattr(settings, 'test_image_filter'):
                self._is_of_type('test_image_filter', dict)
                self.test_image_filter = settings.test_image_filter
            else:
                self.test_image_filter = {}

            if hasattr(settings, 'test_event_filter'):
                self._is_of_type('test_event_filter', dict)
                self.test_event_filter = settings.test_event_filter
            else:
                self.test_event_filter = {}

            if hasattr(settings, 'test_folders'):
                self._is_of_type('test_folders', list)
                self.test_folders = settings.test_folders
                if not self.test_folders:
                    self.test_folders = None
            else:
                self.test_folders = None
            if not self.test_folders:
                self.test_folders = None

            if hasattr(settings, 'dl2_path'):
                self._is_of_type('dl2_path', str)
                self.dl2_path = settings.dl2_path
                if not self.dl2_path:
                    self.dl2_path = None
            else:
                self.dl2_path = None

            if hasattr(settings, 'test_file_max_number'):
                self._is_of_type('test_file_max_number', int)
                self.test_file_max_number = settings.test_file_max_number
            else:
                self.test_file_max_number = None

            if hasattr(settings, 'test_batch_size'):
                self.test_batch_size = settings.test_batch_size
            elif self.batch_size is not None:
                self.test_batch_size = self.batch_size
            else:
                raise ValueError

            if hasattr(settings, 'test_callbacks'):
                self.test_callbacks = settings.test_callbacks
            else:
                self.test_callbacks = []

        else:
            self.test_step = None
            self.test_image_filter = {}
            self.test_event_filter = {}
            self.test_folders = None
            self.test_batch_size = None
            self.test_callbacks = []
            self.test_dataset_parameters = None

    def _has_mandatory(self, parameter, message):
        try:
            assert hasattr(self._settings, parameter)
        except AssertionError as err:
            self._logger.exception('Missing {param} : {msg}'.format(param=parameter, msg=message))
            raise err

    def _is_positive(self, parameter):
        message = 'Specification error on  {param}. It must be set above 0'.format(param=parameter)
        try:
            assert getattr(self._settings, parameter) > 0
        except AssertionError as err:
            self._logger.exception(message)
            raise err

    def _is_of_type(self, parameter, p_type):
        message = 'Specification error on  {param}. It must be of type {type}'.format(param=parameter,
                                                                                      type=p_type)
        try:
            assert isinstance(getattr(self._settings, parameter), p_type)
        except AssertionError as err:
            self._logger.exception(message)
            raise err

    def _is_function(self, parameter, n_args):
        message = 'Specification error on  {param}. It must be a function of {n_args} args'.format(param=parameter,
                                                                                                   n_args=n_args)
        try:
            assert inspect.isfunction(getattr(self._settings, parameter))
        except AssertionError as err:
            self._logger.exception(message)
            raise err
        try:
            assert len(inspect.getfullargspec(getattr(self._settings, parameter))[0]) == n_args
        except AssertionError as err:
            self._logger.exception(message)
            raise err


class LitGLearnModule(LightningModule):

    def __init__(self, experiment):
        super().__init__()
        # TODO save hyperparameters
        # self.save_hyperparameters(dict from experiment)
        self.automatic_optimization = False
        self.experiment = experiment
        self.console_logger = logging.getLogger(__name__)
        self.grad_norm = 0

        # create network
        self.net = self.experiment.model_net(self.experiment.net_parameters_dic, self.experiment.camera_geometry)
        self.console_logger.info(
            'network parameters number : {}'.format(compute_total_parameter_number(self.net))
        )
        self.metrics = torch.nn.ModuleDict()
        for task, param in self.experiment.targets.items():
            self.metrics[task] = torch.nn.ModuleDict()
            for name, metric in param['metrics'].items():
                self.metrics[task][name] = metric

        self.test_data = {'output': [], 'dl1_params': []}

    def forward(self, x):
        return self.net(x)

    def reset_test_data(self):
        self.test_data = {'output': [], 'dl1_params': []}

    def training_step(self, batch, batch_idx):
        optimizers = self.optimizers(use_pl_optimizer=True)
        if isinstance(optimizers, list):
            for optim in optimizers:
                optim.zero_grad()
        else:
            optimizers.zero_grad()

        if self.global_step == 0:
            self.console_logger.info(('Experiment running on {}'.format(self.device)))  # TODO handle multi gpus
            if self.device.type == 'cuda':
                self.console_logger.info('GPU name : {}'.format(torch.cuda.get_device_name(self.device.index)))

        output, labels, loss_data, loss = self.experiment.training_step(self, batch)

        self.manual_backward(loss)

        norm = 0
        for p in list(filter(lambda x: x.grad is not None, self.net.parameters())):
            norm += p.grad.data.norm(2).detach() ** 2
        self.grad_norm = norm ** (1. / 2)

        if isinstance(optimizers, list):
            for optim in optimizers:
                optim.step()
        else:
            optimizers.step()

        # log losses
        if self.global_step == 0:
            self.logger.experiment.add_scalars('Training', {'Loss_' + n: v for n, v in loss_data.items()})
        self.log('Training', {'Loss_' + n: v for n, v in loss_data.items()}, on_step=False, on_epoch=True)
        training_loss = 0
        for v in loss_data.values():
            training_loss += v
        self.log('Loss', {'training': training_loss}, on_step=False, on_epoch=True)
        self.log('Loss_weighted', {'training': loss.detach()}, on_step=False, on_epoch=True)
        # log other metrics
        for task, all_metrics in self.metrics.items():
            for name, metric in all_metrics.items():
                if task == 'class':
                    m_value = metric(torch.exp(output[task]), labels[task])
                else:
                    m_value = metric(output[task], labels[task])
                self.log(name, {'training': m_value}, on_step=False, on_epoch=True)
        # Log in console
        n_batches = len(self.trainer.train_dataloader)
        iteration = self.global_step % n_batches + 1
        if iteration % self.experiment.log_every_n_steps == 0:
            self.console_logger.info('Epoch[{}] Iteration[{}/{}]'.format(self.current_epoch, iteration, n_batches))
            # log losses
            for n, v in loss_data.items():
                self.console_logger.info('Training Loss ' + n + ' {}'.format(v))
            # log other metrics
            for task, all_metrics in self.metrics.items():
                for name, metric in all_metrics.items():
                    if task == 'class':
                        m_value = metric(torch.exp(output[task]), labels[task])
                    else:
                        m_value = metric(output[task], labels[task])
                    self.console_logger.info('Training ' + name + ' {}'.format(m_value))
        return loss

    def training_epoch_end(self, outputs):
        lr_schedulers = self.lr_schedulers()
        if lr_schedulers is not None:
            lr_schedulers = [lr_schedulers] if not isinstance(lr_schedulers, list) else lr_schedulers
            for scheduler in lr_schedulers:
                if isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                    scheduler.step(self.trainer.callback_metrics["Loss_validating"])
                else:
                    scheduler.step()

    def validation_step(self, batch, batch_idx):
        output, labels, loss_data, loss = self.experiment.eval_step(self, batch)
        # log losses
        self.log('Validating', {'Loss_' + n: v for n, v in loss_data.items()})
        val_loss = 0
        for n, v in loss_data.items():
            # self.console_logger.info('Validating ' + n + ' {}'.format(v))
            val_loss += v
        self.log('Loss', {'validating': val_loss})
        self.log('Loss_validating', loss.detach())
        self.log('Loss_weighted', {'validating': loss.detach()})
        # log other metrics
        for task, all_metrics in self.metrics.items():
            for name, metric in all_metrics.items():
                if task == 'class':
                    metric(torch.exp(output[task]), labels[task])
                else:
                    metric(output[task], labels[task])

    def validation_epoch_end(self, *args, **kwargs):
        self.console_logger.info('Epoch[{}] Validation]'.format(self.current_epoch))
        # log other metrics
        for task, all_metrics in self.metrics.items():
            for name, metric in all_metrics.items():
                m_value = metric.compute()
                self.log(name, {'validating': m_value})
                self.console_logger.info('Validating ' + name + ' {}'.format(m_value))

    def test_step(self, batch, batch_idx):
        output, dl1_params = self.experiment.test_step(self, batch)
        self.test_data['output'].append(output)
        self.test_data['dl1_params'].append(dl1_params)

    def configure_optimizers(self):
        optim_keys = self.experiment.optimizer_dic.keys()
        if 'network' in optim_keys:
            assert all(
                key not in optim_keys
                for key in ['feature', 'classifier', 'regressor']
            ), 'If you define an optimizer for the whole network, you cant also define one for a subpart of it.'

        if 'feature' in optim_keys:
            assert 'classifier' in optim_keys or 'regressor' in optim_keys, \
                'You need an optimizer for every subparts of the net.'

        optimizers = {}
        for key in self.experiment.optimizer_dic.keys():
            if key == 'network':
                optimizers[key] = self.experiment.optimizer_dic[key](self.net,
                                                                     self.experiment.optimizer_parameters[key])
            elif key == 'feature':
                optimizers[key] = self.experiment.optimizer_dic[key](self.net.feature,
                                                                     self.experiment.optimizer_parameters[key])
            elif key == 'classifier':
                optimizers[key] = self.experiment.optimizer_dic[key](self.net.classifier,
                                                                     self.experiment.optimizer_parameters[key])
            elif key == 'regressor':
                optimizers[key] = self.experiment.optimizer_dic[key](self.net.regressor,
                                                                     self.experiment.optimizer_parameters[key])
            elif key == 'loss_balancing':
                assert isinstance(self.experiment.compute_loss, torch.nn.Module)
                optimizers[key] = self.experiment.optimizer_dic[key](self.experiment.compute_loss,
                                                                     self.experiment.optimizer_parameters[key])

        if self.experiment.lr_schedulers is not None:
            schedulers = []
            for scheduler, options in self.experiment.lr_schedulers.items():
                for net_param, scheduler_param in options.items():
                    if optimizers[net_param] is not None:
                        schedulers.append(scheduler(optimizers[net_param], **scheduler_param))
        else:
            schedulers = None

        return list(optimizers.values()), schedulers


def main():
    # For better performance (if the input size does not vary from a batch to another)
    cudnn.benchmark = True

    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger('gammalearn')

    # Parse script arguments
    logger.info('parse arguments')
    parser = argparse.ArgumentParser()
    parser.add_argument("configuration_file", help="path to configuration file")
    parser.add_argument('--fast_debug', help='log useful information for debug purpose',
                        action='store_true')
    parser.add_argument("--logfile", help="whether to write the log on disk", action="store_true")
    parser.add_argument('--version', action='version', version=_version)

    args = parser.parse_args()
    configuration_file = args.configuration_file
    fast_debug = args.fast_debug
    logfile = args.logfile

    # Update logging config
    LOGGING_CONFIG['handlers']['console']['formatter'] = 'console_debug' if fast_debug else 'console_info'
    LOGGING_CONFIG['loggers']['gammalearn']['level'] = 'DEBUG' if fast_debug else 'INFO'
    logging.config.dictConfig(LOGGING_CONFIG)

    logger = logging.getLogger('gammalearn')

    # load settings file
    logger.info(f'load settings from {configuration_file}')
    spec = importlib.util.spec_from_file_location("settings", configuration_file)
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)

    # check config and prepare experiment
    experiment = Experiment(settings)

    # prepare folders
    logger.info('prepare folders')
    prepare_experiment_folder(experiment.main_directory, experiment.experiment_name)

    if logfile:
        LOGGING_CONFIG['handlers']['file'] = {
            'class': 'logging.FileHandler',
            'filename': '{}/{}/{}.log'.format(settings.main_directory,
                                              settings.experiment_name,
                                              settings.experiment_name),
            'mode': 'w',
            'formatter': 'detailed_debug' if fast_debug else 'detailed_info'
        }
        LOGGING_CONFIG['loggers']['gammalearn']['handlers'].append('file')
        logging.config.dictConfig(LOGGING_CONFIG)

    logger.info('gammalearn {}'.format(_version))
    # save config(settings)
    logger.info('save configuration file')
    shutil.copyfile(configuration_file, '{}/{}/{}_settings.py'.format(experiment.main_directory,
                                                                      experiment.experiment_name,
                                                                      experiment.experiment_name))
    # dump settings
    dump_experiment_config(experiment)

    # prepare tensorboard logger
    tb_directory = experiment.main_directory + '/runs/'
    run_directory = tb_directory + experiment.experiment_name
    if not os.path.exists(run_directory):
        os.makedirs(run_directory)
        os.chmod(run_directory, 0o775)
    logger.info('Tensorboard run directory: {} '.format(run_directory))
    tb_logger = TensorBoardLogger(tb_directory, experiment.experiment_name)

    # set seed
    if experiment.random_seed is not None:
        pl.trainer.seed_everything(experiment.random_seed)

    # Load data module
    gl_data_module = GLearnDataModule(experiment)
    gl_data_module.setup()

    geometries = []
    get_dataset_geom(gl_data_module.train_set, geometries)
    get_dataset_geom(gl_data_module.test_sets, geometries)
    # testing if all geometries are equal
    if len(set(geometries)) != 1:
        raise WrongGeometryError("There are different geometries in the train and the test datasets")

    experiment.camera_geometry = geometries[0]

    # Define multiprocessing start method
    try:
        assert torch.multiprocessing.get_start_method() == experiment.mp_start_method
    except AssertionError:
        torch.multiprocessing.set_start_method(experiment.mp_start_method, force=True)
    logger.info('mp start method: {}'.format(torch.multiprocessing.get_start_method()))

    # Reset seed
    if experiment.random_seed is not None:
        pl.trainer.seed_everything(experiment.random_seed)

    logger.info('Save net definition file')
    shutil.copyfile(experiment.net_definition_file, '{}/{}/nets.py'.format(experiment.main_directory,
                                                                           experiment.experiment_name))

    # load lightning module
    gl_lightning_module = LitGLearnModule(experiment)

    checkpoint_callback = ModelCheckpoint(dirpath=os.path.join(experiment.main_directory, experiment.experiment_name),
                                          monitor='Loss_validating', filename='checkpoint_{epoch}',
                                          every_n_epochs=experiment.save_every, save_top_k=-1)

    # Log learning rates
    callbacks = [
        checkpoint_callback,
        LearningRateMonitor(logging_interval='epoch'),
        DeviceStatsMonitor()
    ]

    callbacks.extend(experiment.training_callbacks)
    callbacks.extend(experiment.test_callbacks)

    # Prepare profiler
    if experiment.profiler is not None:
        profiler = experiment.profiler['profiler'](
            dirpath=os.path.join(experiment.main_directory, experiment.experiment_name),
            filename=os.path.join(experiment.experiment_name + '.prof'),
            **experiment.profiler['options']
        )
    else:
        profiler = None

    # Run !
    if fast_debug:
        trainer = pl.Trainer(fast_dev_run=True, gpus=-1, strategy=experiment.ddp, profiler=profiler)
        trainer.fit(gl_lightning_module,
                    train_dataloaders=gl_data_module.train_dataloader(),
                    val_dataloaders=gl_data_module.val_dataloader())
        # TODO remove when lightning bug is fixed
        if experiment.profiler is not None:
            profiler = experiment.profiler['profiler'](
                dirpath=os.path.join(experiment.main_directory, experiment.experiment_name),
                filename=os.path.join(experiment.experiment_name + '.prof'),
                **experiment.profiler['options'])
            trainer.profiler = profiler

        trainer.test(gl_lightning_module,
                     dataloaders=gl_data_module.test_dataloader())
    else:
        trainer = pl.Trainer(
            default_root_dir=os.path.join(experiment.main_directory, experiment.experiment_name),
            gpus=experiment.gpus, strategy=experiment.ddp, max_epochs=experiment.max_epochs,
            resume_from_checkpoint=experiment.checkpoint_path, logger=tb_logger,
            log_every_n_steps=experiment.log_every_n_steps,
            check_val_every_n_epoch=experiment.check_val_every_n_epoch,
            callbacks=callbacks, profiler=profiler
        )

        if experiment.train:
            logger.info('Train model')
            trainer.fit(gl_lightning_module,
                        train_dataloaders=gl_data_module.train_dataloader(),
                        val_dataloaders=gl_data_module.val_dataloader())
            if experiment.test:
                logger.info('Test model')
                for dataloader in gl_data_module.test_dataloaders():
                    # TODO remove when lightning bug is fixed
                    if experiment.profiler is not None:
                        profiler = experiment.profiler['profiler'](
                            dirpath=os.path.join(experiment.main_directory, experiment.experiment_name),
                            filename=os.path.join(experiment.experiment_name + '.prof'),
                            **experiment.profiler['options'])
                        trainer.profiler = profiler

                    trainer.test(gl_lightning_module,
                                 dataloaders=dataloader)
                    gl_lightning_module.reset_test_data()
        elif experiment.test:
            logger.info('Test model')
            assert experiment.checkpoint_path is not None, 'To test a model w/o training, there must be a checkpoint'
            map_location = torch.device('cpu') if experiment.gpus == 0 else None
            ckpt = torch.load(experiment.checkpoint_path, map_location=map_location)
            gl_lightning_module.load_state_dict(ckpt['state_dict'])
            for dataloader in gl_data_module.test_dataloaders():
                # TODO remove when lightning bug is fixed
                if experiment.profiler is not None:
                    profiler = experiment.profiler['profiler'](
                        dirpath=os.path.join(experiment.main_directory, experiment.experiment_name),
                        filename=os.path.join(experiment.experiment_name + '.prof'),
                        **experiment.profiler['options'])
                    trainer.profiler = profiler

                trainer.test(gl_lightning_module, dataloaders=dataloader)
                gl_lightning_module.reset_test_data()


if __name__ == '__main__':
    main()
