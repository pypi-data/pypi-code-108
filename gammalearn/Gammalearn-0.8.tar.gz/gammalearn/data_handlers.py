import logging
import torch.multiprocessing as mp
from functools import partial

from pytorch_lightning import LightningDataModule
import torch
from torch.utils.data import DataLoader, Dataset, ConcatDataset, Subset
from torchvision import transforms

from gammalearn import utils as utils
from gammalearn.logging import LOGGING_CONFIG


def create_dataset_worker(file,
                          data_transform,
                          dataset_class,
                          targets,
                          dataset_parameters,
                          image_filter,
                          event_filter,
                          train):
    torch.set_num_threads(1)
    # Reload logging config (lost by spawn)
    logging.config.dictConfig(LOGGING_CONFIG)

    if data_transform is not None:
        transform = transforms.Compose(data_transform['data'])
        target_transform = transforms.Compose(data_transform['target'])
    else:
        transform = None
        target_transform = None

    if utils.is_datafile_healthy(file):
        dataset = dataset_class(file,
                                targets=targets,
                                transform=transform,
                                target_transform=target_transform,
                                **dataset_parameters,
                                train=train
                                )
        if image_filter is not None:
            dataset.filter_image(image_filter)
        if event_filter is not None:
            dataset.filter_event(event_filter)
        if len(dataset) > 0:
            return dataset


def create_datasets(datafiles_list, experiment, train=True):
    """
    Create datasets from datafiles list, data are loaded in memory.
    Parameters
    ----------
    datafiles (List) : files to load data from
    experiment (Experiment): the experiment

    Returns
    -------
    Datasets
    """
    logger = logging.getLogger('gammalearn')
    assert datafiles_list, 'The data file list is empty !'

    logger.info('length of data file list : {}'.format(len(datafiles_list)))
    # We get spawn context because fork can cause deadlock in sub-processes
    # in multi-threaded programs (especially with logging)
    ctx = mp.get_context('spawn')
    if experiment.preprocessing_workers > 0:
        num_workers = experiment.preprocessing_workers
    else:
        num_workers = 1
    pool = ctx.Pool(processes=num_workers)
    datasets = pool.map(partial(create_dataset_worker,
                                data_transform=experiment.data_transform,
                                dataset_class=experiment.dataset_class,
                                targets=list(experiment.targets.keys()),
                                dataset_parameters=experiment.dataset_parameters,
                                image_filter=experiment.image_filter,
                                event_filter=experiment.event_filter,
                                train=train),
                        datafiles_list)

    return datasets


def split_dataset(datasets, ratio, split_by_file=False):
    """Split a list of datasets into a train and a validation set
    Parameters
    ----------
    datasets (list of Dataset): the list of datasets
    ratio (float): the ratio of data for validation
    split_by_file (bool): whether to divide at the file or at the sample level

    Returns
    -------
    train set, validation set

    """
    # Creation of subset train and test
    assert 1 > ratio > 0, 'Validating ratio must be greater than 0 and smaller than 1.'
    if split_by_file:
        train_max_index = int(len(datasets) * (1 - ratio))
        shuffled_indices = torch.randperm(len(datasets)).numpy()
        train_datasets = [datasets[i] for i in shuffled_indices[:train_max_index]]
        val_datasets = [datasets[i] for i in shuffled_indices[train_max_index:]]
    else:
        datasets = ConcatDataset(datasets)
        train_max_index = int(len(datasets) * (1 - ratio))
        shuffled_indices = torch.randperm(len(datasets)).numpy()
        assert isinstance(datasets, Dataset)
        train_datasets = [Subset(datasets, shuffled_indices[:train_max_index])]
        val_datasets = [Subset(datasets, shuffled_indices[train_max_index:])]

    return train_datasets, val_datasets


class GLearnDataModule(LightningDataModule):
    """
    Create datasets and dataloaders.
    Parameters
    ----------
    experiment (Experiment): the experiment

    Returns
    -------
    """
    def __init__(self, experiment):
        super().__init__()
        self.experiment = experiment
        self.logger = logging.getLogger(__name__)
        self.train_set = None
        self.val_set = None
        self.test_sets = None

    def setup(self, stage=None):

        self.logger.info('Start creating datasets')

        if self.experiment.train:
            self.logger.info('look for data files')
            train_file_list = utils.find_datafiles(self.experiment.train_folders, self.experiment.files_max_number)
            self.logger.debug(train_file_list)
            train_file_list = list(train_file_list)
            train_file_list.sort()
            datasets = create_datasets(train_file_list, self.experiment)

            assert datasets, 'Dataset is empty !'

            # Creation of subset train and test
            train_datasets, val_datasets = split_dataset(datasets, self.experiment.validating_ratio,
                                                         self.experiment.split_by_file)

            if self.experiment.data_augment is not None:
                self.logger.info('Start data augmentation')
                train_datasets = self.experiment.data_augment['function'](train_datasets,
                                                                          **self.experiment.data_augment['kwargs'])
            self.train_set = ConcatDataset(train_datasets)
            self.logger.info('training set length : {}'.format(len(self.train_set)))

            self.val_set = ConcatDataset(val_datasets)
            try:
                assert len(self.val_set) > 0
            except AssertionError as e:
                self.logger.exception('Validating set must contain data')
                raise e
            self.logger.info('validating set length : {}'.format(len(self.val_set)))
        else:
            self.train_set = None
            self.val_set = None
        if self.experiment.test:
            if self.experiment.test_folders is not None:
                # Look for specific data parameters
                if self.experiment.test_dataset_parameters is not None:
                    self.experiment.dataset_parameters.update(self.experiment.test_dataset_parameters)
                # Update data filters
                self.experiment.image_filter = self.experiment.test_image_filter
                self.experiment.event_filter = self.experiment.test_event_filter
                # Create data sets
                test_file_list = utils.find_datafiles(self.experiment.test_folders,
                                                      self.experiment.test_file_max_number)
                test_file_list = list(test_file_list)
                test_file_list.sort()
                self.test_sets = create_datasets(test_file_list, self.experiment, train=False)
            else:
                assert self.val_set is not None, 'Test is required but no test file is provided and val_set is None'
                self.test_sets = [self.val_set]
            self.logger.info('test set length : {}'.format(torch.tensor([len(t) for t in self.test_sets]).sum()))

    def train_dataloader(self):
        training_loader = DataLoader(self.train_set,
                                     batch_size=self.experiment.batch_size,
                                     shuffle=True,
                                     drop_last=True,
                                     num_workers=self.experiment.dataloader_workers,
                                     pin_memory=self.experiment.pin_memory)
        self.logger.info('training loader length : {} batches'.format(len(training_loader)))
        return training_loader

    def val_dataloader(self):
        validating_loader = DataLoader(self.val_set,
                                       batch_size=self.experiment.batch_size,
                                       shuffle=False,
                                       num_workers=self.experiment.dataloader_workers,
                                       drop_last=False,
                                       pin_memory=self.experiment.pin_memory)
        self.logger.info('validating loader length : {} batches'.format(len(validating_loader)))
        return validating_loader

    def test_dataloaders(self):
        test_loaders = [DataLoader(test_set, batch_size=self.experiment.test_batch_size, shuffle=False,
                                   drop_last=False, num_workers=self.experiment.dataloader_workers)
                        for test_set in self.test_sets]
        self.logger.info('test loader length : {} batches'.format(torch.tensor([len(t) for t in test_loaders]).sum()))
        return test_loaders
