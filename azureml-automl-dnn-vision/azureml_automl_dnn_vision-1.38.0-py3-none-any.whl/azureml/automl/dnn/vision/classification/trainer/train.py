# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Training functions."""
import copy
import gc
import time
from contextlib import nullcontext
from typing import Any, Callable, Dict, Optional, Tuple

import torch
from torchvision import transforms

import azureml
from azureml.automl.runtime.shared.score.scoring import constants as scoring_constants
from azureml.automl.dnn.vision.classification.common.classification_utils import log_classification_metrics
from azureml.automl.dnn.vision.classification.common.constants import TrainingLiterals
from azureml.automl.dnn.vision.classification.common.transforms import _get_common_train_transforms, \
    _get_common_valid_transforms
from azureml.automl.dnn.vision.classification.io.read.dataloader import _get_data_loader
from azureml.automl.dnn.vision.classification.io.read.dataset_wrappers import AmlDatasetWrapper
from azureml.automl.dnn.vision.classification.io.write.score_script_utils import write_scoring_script
from azureml.automl.dnn.vision.classification.models import ModelFactory
from azureml.automl.dnn.vision.classification.trainer.criterion import _get_criterion
from azureml.automl.dnn.vision.common import distributed_utils, utils as common_utils
from azureml.automl.dnn.vision.common.artifacts_utils import save_model_checkpoint, write_artifacts, \
    load_from_pretrained_checkpoint
from azureml.automl.dnn.vision.common.average_meter import AverageMeter
from azureml.automl.dnn.vision.common.constants import MetricsLiterals, \
    SettingsLiterals as CommonSettingsLiterals, TrainingLiterals as CommonTrainingLiterals
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionDataException, AutoMLVisionSystemException
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.system_meter import SystemMeter
from azureml.automl.dnn.vision.common.trainer.lrschedule import LRSchedulerUpdateType, setup_lr_scheduler
from azureml.automl.dnn.vision.common.trainer.optimize import setup_optimizer
from azureml.automl.dnn.vision.metrics import ClassificationMetrics
from azureml.core import Run, Workspace

logger = get_logger(__name__)


def train_one_epoch(model_wrapper: 'azureml.automl.dnn.vision.classification.models.'
                                   'classification_model_wrappers.ModelWrapper',
                    epoch: int, dataloader: Any, criterion: Any, optimizer: Any, device: Any, lr_scheduler: Any,
                    multilabel: bool, system_meter: Any, distributed: bool, metrics: Any,
                    grad_accum_steps: int, grad_clip_type: str) -> float:
    """Train a model for one epoch

    :param model_wrapper: Model to be trained
    :type model_wrapper: <class 'vision.classification.models.classification_model_wrappers.ModelWrapper'>
    :param epoch: Current training epoch
    :type epoch: int
    :param dataloader: dataloader for training dataset
    :type dataloader: <class 'vision.common.dataloaders.RobustDataLoader'>
    :param criterion: loss function
    :type criterion: <class 'torch.nn.modules.loss.CrossEntropyLoss'>
    :param optimizer: Optimizer to update model weights
    :type optimizer: Pytorch optimizer
    :param device: target device
    :type device: <class 'torch.device'>
    :param lr_scheduler: learning rate scheduler
    :type lr_scheduler: <class 'dnn.vision.common.trainer.lrschedule.lrscheduleWrapper'>
    :param multilabel: boolean flag for multilabel
    :type multilabel: bool
    :param system_meter: A SystemMeter to collect system properties
    :type system_meter: SystemMeter
    :param distributed: Training in distributed mode or not
    :type distributed: bool
    :param metrics: metrics to evaluate on training dataset
    :type metrics: <class 'vision.metrics.classification_metrics.ClassificationMetrics'>
    :param grad_accum_steps: gradient accumulation steps which is used to accumulate the gradients of those steps
     without updating model variables/weights
    :type grad_accum_steps: int
    :param clip_type: The type of gradient clipping. See GradClipType
    :type grad_clip_type: str
    :return: training epoch loss
    :rtype: float
    """
    batch_time = AverageMeter()

    data_time = AverageMeter()
    losses = AverageMeter()
    top1 = AverageMeter()

    total_outputs_list = []
    total_labels_list = []

    model_wrapper.model.train()

    # grad_accum_steps should be positive, smaller or equal than the number of batches per epoch
    grad_accum_steps = min(len(dataloader), max(grad_accum_steps, 1))
    logger.info("[grad_accumulation_step: {}]".format(grad_accum_steps))
    optimizer.zero_grad()

    end = time.time()
    uneven_batches_context_manager = model_wrapper.model.join() if distributed else nullcontext()

    with uneven_batches_context_manager:
        for i, (inputs, labels) in enumerate(common_utils._data_exception_safe_iterator(iter(dataloader))):
            # measure data loading time
            data_time.update(time.time() - end)

            inputs = inputs.to(device)
            labels = labels.to(device)

            outputs = model_wrapper.model(inputs)
            total_outputs_list.append(outputs)
            total_labels_list.append(labels)

            loss = criterion(outputs, labels)
            loss /= grad_accum_steps
            loss_value = loss.item()
            # raise an UserException if loss is too big
            common_utils.check_loss_explosion(loss_value)
            loss.backward()

            if (i + 1) % grad_accum_steps == 0 or i == len(dataloader) - 1:
                # gradient clipping
                common_utils.clip_gradient(model_wrapper.model.parameters(), grad_clip_type)
                optimizer.step()
                optimizer.zero_grad()

            if not multilabel:
                # record loss and measure elapsed time
                prec1 = common_utils._accuracy(outputs.data, labels)
                top1.update(prec1[0][0], inputs.size(0))

            if lr_scheduler.update_type == LRSchedulerUpdateType.BATCH:
                lr_scheduler.lr_scheduler.step()

            losses.update(loss_value, inputs.size(0))
            batch_time.update(time.time() - end)
            end = time.time()

            # delete tensors which have a valid grad_fn
            del loss, outputs

            if i % 100 == 0 or i == len(dataloader) - 1:
                msg = "Epoch: [{0}][{1}/{2}]\t" "lr: {3}\t" "Time {batch_time.value:.4f} ({batch_time.avg:.4f})\t"\
                      "Data {data_time.value:.4f} ({data_time.avg:.4f})\t" "Loss {loss.value:.4f} " \
                      "({loss.avg:.4f})".format(epoch, i, len(dataloader), optimizer.param_groups[0]["lr"],
                                                batch_time=batch_time, data_time=data_time, loss=losses)
                if not multilabel:
                    msg += "\tAcc@1 {top1.value:.3f} ({top1.avg:.3f})".format(top1=top1)
                logger.info(msg)

                system_meter.log_system_stats()

    if lr_scheduler.update_type == LRSchedulerUpdateType.EPOCH:
        lr_scheduler.lr_scheduler.step()

    _update_metrics(distributed, metrics, total_outputs_list, total_labels_list, model_wrapper, is_train=True)

    return losses.avg


def _update_metrics(distributed: bool, metrics: Any, total_outputs_list: Any, total_labels_list: Any,
                    model_wrapper: Any, is_train: bool) -> None:
    """Update metrics with model predictions

    :param distributed: Training in distributed mode or not
    :type distributed: bool
    :param metrics: metrics to evaluate on training or validation dataset
    :type metrics: <class 'vision.metrics.classification_metrics.ClassificationMetrics'>
    :param total_outputs_list: model predictions
    :type total_outputs_list: list
    :param total_labels_list: target labels
    :type total_labels_list: list
    :param model_wrapper: Model to evaluate validation data with
    :type model_wrapper: <class 'vision.classification.models.classification_model_wrappers.ModelWrapper'>
    :param is_train: flag indicating whether the metric is computed with training data or not.
    :type is_train: bool
    """
    metrics.reset(is_train=is_train)

    if not total_labels_list:
        exception_message = "All images in the data set processed by worker {} are invalid. " \
                            "Cannot compute primary metric.".format(
                                distributed_utils.get_rank())
        raise AutoMLVisionDataException(exception_message, has_pii=False)

    if distributed:
        # Gather metrics data from other workers.
        outputs_list = distributed_utils.all_gather_uneven_tensors(
            torch.cat(total_outputs_list))
        labels_list = distributed_utils.all_gather_uneven_tensors(
            torch.cat(total_labels_list))
        if len(outputs_list) != len(labels_list):
            raise AutoMLVisionSystemException("Outputs list is of size {} and labels list is of size {}. "
                                              "Both lists should be of same size after all_gather."
                                              .format(len(outputs_list), len(labels_list)), has_pii=False)

        for index, outputs in enumerate(outputs_list):
            probs = model_wrapper.predict_probs_from_outputs(outputs)
            metrics.update(
                probs=probs, labels=labels_list[index], is_train=is_train)

    else:
        probs = model_wrapper.predict_probs_from_outputs(
            torch.cat(total_outputs_list))
        metrics.update(probs=probs, labels=torch.cat(
            total_labels_list), is_train=is_train)


def validate(model_wrapper: Any, epoch: int, dataloader: Any = None, criterion: Any = None, metrics: Any = None,
             device: Any = None, multilabel: bool = False, system_meter: Any = None,
             distributed: bool = False) -> float:
    """Gets model results on validation set.

    :param model_wrapper: Model to evaluate validation data with
    :type model_wrapper: <class 'vision.classification.models.classification_model_wrappers.ModelWrapper'>
    :param epoch: Current training epoch
    :type epoch: int
    :param dataloader: dataloader for training dataset
    :type dataloader: <class 'vision.common.dataloaders.RobustDataLoader'>
    :param criterion: loss function
    :type criterion: <class 'torch.nn.modules.loss.CrossEntropyLoss'>
    :param metrics: metrics to evaluate on validation dataset
    :type metrics: <class 'vision.metrics.classification_metrics.ClassificationMetrics'>
    :param device: target device
    :type device: <class 'torch.device'>
    :param multilabel: boolean flag for multilabel
    :type multilabel: bool
    :param system_meter: A SystemMeter to collect system properties
    :type system_meter: SystemMeter
    :param distributed: Training in distributed mode or not
    :type distributed: bool
    :return: validation epoch loss
    :rtype: float
    """
    batch_time = AverageMeter()
    top1 = AverageMeter()
    data_time = AverageMeter()
    val_losses = AverageMeter()

    model_wrapper.model.eval()

    total_outputs_list = []
    total_labels_list = []

    end = time.time()
    with torch.no_grad():
        for i, (inputs, labels) in enumerate(common_utils._data_exception_safe_iterator(iter(dataloader))):
            # measure data loading time
            data_time.update(time.time() - end)

            inputs = inputs.to(device)
            labels = labels.to(device)

            # We have observed that pytorch DDP does some AllReduce calls during eval model as well.
            # When there are uneven number of batches across worker processes, there is issue with mismatch
            # of distributed calls between processes and it leads to blocked processes and hangs.
            # Using the pytorch model instead of DDP model to run validation to avoid sync calls during eval.
            # One other observation is that AllReduce calls from DDP are only seen when we use .join() during
            # training phase.
            base_torch_model = model_wrapper.model.module if distributed else model_wrapper.model
            outputs = base_torch_model(inputs)
            val_loss = criterion(outputs, labels)
            val_loss_value = val_loss.item()
            val_losses.update(val_loss_value, inputs.size(0))

            total_outputs_list.append(outputs)
            total_labels_list.append(labels)

            if not multilabel:
                prec1 = common_utils._accuracy(outputs.data, labels)
                top1.update(prec1[0][0], inputs.size(0))

            # measure elapsed time
            batch_time.update(time.time() - end)
            end = time.time()

            if i % 100 == 0 or i == len(dataloader) - 1:
                mesg = "Test Epoch: [{0}][{1}/{2}]\t" \
                       "Time {batch_time.value:.4f} ({batch_time.avg:.4f})\t" \
                       "Data {data_time.value:.4f} ({data_time.avg:.4f})\t" \
                       "Loss {loss.value:.4f} ({loss.avg:.4f})".\
                    format(epoch, i, len(dataloader), batch_time=batch_time,
                           data_time=data_time, loss=val_losses)
                if not multilabel:
                    mesg += "\tAcc@1 {top1.value:.3f} ({top1.avg:.3f})".format(
                        top1=top1)
                logger.info(mesg)

                if system_meter is not None:
                    system_meter.log_system_stats()

    _update_metrics(distributed, metrics, total_outputs_list, total_labels_list, model_wrapper, is_train=False)

    return val_losses.avg


def _validate_score_run(model_wrapper: Any, run: Run, device: Any, workspace: Workspace,
                        batch_size: int = 80, ignore_data_errors: bool = True,
                        input_dataset_id: Optional[str] = None, num_workers: Optional[int] = None) -> None:
    logger.info("Validation flag was passed. Starting validation.")
    multilabel = model_wrapper.multilabel
    valid_sys_meter = SystemMeter()
    valid_dataset_wrapper = AmlDatasetWrapper(input_dataset_id,
                                              multilabel=multilabel,
                                              workspace=workspace,
                                              download_files=False,
                                              ignore_data_errors=ignore_data_errors)

    valid_resize_size = model_wrapper.valid_resize_size,
    valid_crop_size = model_wrapper.valid_crop_size
    valid_transforms = _get_common_valid_transforms(resize_to=valid_resize_size, crop_size=valid_crop_size)

    valid_dataloader = _get_data_loader(valid_dataset_wrapper,
                                        transform_fn=valid_transforms,
                                        batch_size=batch_size,
                                        num_workers=num_workers,
                                        distributed=False)

    metrics = ClassificationMetrics(labels=valid_dataset_wrapper.labels, multilabel=multilabel)

    epoch_val_loss = validate(model_wrapper, epoch=0, dataloader=valid_dataloader,
                              criterion=_get_criterion(multilabel=multilabel),
                              metrics=metrics, device=device,
                              multilabel=multilabel, system_meter=valid_sys_meter,
                              distributed=False)

    computed_metrics = metrics.compute(is_train=False)
    computed_metrics[MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS][scoring_constants.LOG_LOSS] = epoch_val_loss

    primary_metric = MetricsLiterals.IOU if multilabel else MetricsLiterals.ACCURACY

    log_classification_metrics(metrics, computed_metrics, primary_metric,
                               azureml_run=run, final_epoch=True,
                               best_model_metrics=computed_metrics)


def _get_train_test_dataloaders(dataset: 'azureml.automl.dnn.vision.io.read.DatasetWrapper',
                                valid_dataset: 'azureml.automl.dnn.vision.io.read.DatasetWrapper',
                                valid_resize_size: int, valid_crop_size: int, train_crop_size: int,
                                train_transforms: Optional[Callable[[], transforms.Compose]],
                                valid_transforms: Optional[Callable[[], transforms.Compose]],
                                batch_size: int, validation_batch_size: int, num_workers: int, distributed: bool) -> \
        Tuple['azureml.automl.dnn.vision.common.dataloader.RobustDataLoader',
              'azureml.automl.dnn.vision.common.dataloader.RobustDataLoader']:
    """Setup dataloaders for train and validation datasets

    :param dataset: datasetwrapper object for training
    :type dataset: azureml.automl.dnn.vision.io.read.DatasetWrapper
    :param valid_dataset: datasetwrapper object for validation
    :type valid_dataset: azureml.automl.dnn.vision.io.read.DatasetWrapper
    :param valid_resize_size: length of side of the square that we have to resize to
    :type valid_resize_size: int
    :param valid_crop_size: length of side of the square that we have to crop for passing to model
    :type validcrop_size: int
    :param train_crop_size: final input size to crop the image to for train dataset
    :type train_crop_size: int
    :param train_transforms: transformation function to apply to a pillow image object
    :type train_transforms: function
    :param valid_transforms: transformation function to apply to a pillow image object
    :type valid_transforms: function
    :param batch_size: batch size for training dataset
    :type batch_size: int
    :param validation_batch_size: batch size for validation dataset
    :type validation_batch_size: int
    :param num_workers: num workers for dataloader
    :type num_workers: int
    :param distributed: Whether to use distributed data loader.
    :type distributed: bool
    :return: train dataloader and validation dataloader
    :rtype: Tuple[vision.common.dataloaders.RobustDataLoader, vision.common.dataloaders.RobustDataLoader]
    """

    if train_transforms is None:
        train_transforms = _get_common_train_transforms(crop_size=train_crop_size)

    if valid_transforms is None:
        valid_transforms = _get_common_valid_transforms(resize_to=valid_resize_size, crop_size=valid_crop_size)

    train_dataloader = _get_data_loader(dataset, is_train=True, transform_fn=train_transforms,
                                        batch_size=batch_size, num_workers=num_workers, distributed=distributed)
    valid_dataloader = _get_data_loader(valid_dataset, transform_fn=valid_transforms,
                                        batch_size=validation_batch_size,
                                        num_workers=num_workers, distributed=distributed)

    return train_dataloader, valid_dataloader


def _compute_class_weight(dataset_wrapper: 'azureml.automl.dnn.vision.io.read.dataset_wrapper.'
                                           'BaseDatasetWrapper',
                          sqrt_pow: int, device: Optional[str] = None) -> \
        Tuple[int, torch.Tensor]:
    """Calculate imbalance rate and class weights for weighted loss to mitigate class imbalance problem

    :param dataset_wrapper: dataset wrapper
    :type dataset_wrapper: azureml.automl.dnn.vision.io.read.dataset_wrapper.BaseDatasetWrapper
    :param sqrt_pow: square root power when calculating class_weights
    :type sqrt_pow: int
    :param device: device where model should be run (usually "cpu" or "cuda:0" if it is the first gpu)
    :type device: str
    :return: class imbalance ratio and class-level rescaling weights for loss function
    :rtype: Tuple[int, torch.Tensor]
    """

    label_freq_dict = dataset_wrapper.label_freq_dict
    label_freq_list = [0] * dataset_wrapper.num_classes
    for key, val in label_freq_dict.items():
        label_idx = dataset_wrapper.label_to_index_map[key]
        label_freq_list[label_idx] = val

    weights = torch.FloatTensor(label_freq_list).to(device)
    if dataset_wrapper.multilabel:
        # weights in this case are pos_weights
        # pos_weight > 1 increases the recall, pos_weight < 1 increases the precision
        neg_weights = len(dataset_wrapper) - weights
        class_weights = neg_weights / weights
    else:
        class_weights = 1. / weights

    class_weights[class_weights == float("Inf")] = 0
    # sqrt_pow of 2 gives larger variance in class weights than sqrt_pow of 1 in class_weights.
    # In general, class weighting tends to give higher per-class metric but with lower per-instance metrics
    class_weights = torch.sqrt(class_weights) ** sqrt_pow
    logger.info("[class_weights: {}]".format(class_weights))

    imbalance_rate = max(label_freq_list) // max(1, min(label_freq_list))
    return imbalance_rate, class_weights


def train(dataset_wrapper: 'azureml.automl.dnn.vision.io.read.DatasetWrapper',
          valid_dataset: 'azureml.automl.dnn.vision.io.read.DatasetWrapper', settings: Dict[str, Any],
          device: torch.device, train_transforms: Optional[Callable[[], transforms.Compose]] = None,
          valid_transforms: Optional[Callable[[], transforms.Compose]] = None,
          output_dir: str = "", azureml_run: Run = None) -> Any:
    """Train a model

    :param dataset_wrapper: datasetwrapper object for training
    :type dataset_wrapper: azureml.automl.dnn.vision.io.read.DatasetWrapper
    :param valid_dataset: datasetwrapper object for validation
    :type valid_dataset: azureml.automl.dnn.vision.io.read.DatasetWrapper
    :param settings: dictionary containing settings for training
    :type settings: dict
    :param device: device where model should be run (usually "cpu" or "cuda:0" if it is the first gpu)
    :type device: str
    :param train_transforms: transformation function to apply to a pillow image object
    :type train_transforms: function
    :param valid_transforms: transformation function to apply to a pillow image object
    :type valid_transforms: function
    :param output_dir: output directory
    :type output_dir: str
    :param azureml_run: azureml run object
    :type azureml_run: azureml.core.Run
    :return: model settings
    :rtype: dict
    """
    # Extract relevant parameters from training settings
    task_type = settings[CommonSettingsLiterals.TASK_TYPE]
    model_name = settings[CommonSettingsLiterals.MODEL_NAME]
    multilabel = settings.get(CommonSettingsLiterals.MULTILABEL, False)
    num_workers = settings[CommonSettingsLiterals.NUM_WORKERS]
    primary_metric = settings[CommonTrainingLiterals.PRIMARY_METRIC]
    training_batch_size = settings[CommonTrainingLiterals.TRAINING_BATCH_SIZE]
    validation_batch_size = settings[CommonTrainingLiterals.VALIDATION_BATCH_SIZE]
    number_of_epochs = settings[CommonTrainingLiterals.NUMBER_OF_EPOCHS]
    enable_onnx_norm = settings[CommonSettingsLiterals.ENABLE_ONNX_NORMALIZATION]
    log_verbose_metrics = settings.get(CommonSettingsLiterals.LOG_VERBOSE_METRICS, False)
    is_enabled_early_stopping = settings[CommonTrainingLiterals.EARLY_STOPPING]
    early_stopping_patience: int = settings[CommonTrainingLiterals.EARLY_STOPPING_PATIENCE]
    early_stopping_delay = settings[CommonTrainingLiterals.EARLY_STOPPING_DELAY]
    eval_freq = settings[CommonTrainingLiterals.EVALUATION_FREQUENCY]
    checkpoint_freq = settings.get(CommonTrainingLiterals.CHECKPOINT_FREQUENCY, None)
    grad_accum_steps = settings[CommonTrainingLiterals.GRAD_ACCUMULATION_STEP]
    grad_clip_type = settings[CommonTrainingLiterals.GRAD_CLIP_TYPE]

    save_as_mlflow = settings[CommonSettingsLiterals.SAVE_MLFLOW]

    distributed = distributed_utils.dist_available_and_initialized()
    master_process = distributed_utils.master_process()
    rank = distributed_utils.get_rank()

    model_wrapper = ModelFactory().get_model_wrapper(model_name,
                                                     num_classes=dataset_wrapper.num_classes,
                                                     multilabel=multilabel,
                                                     device=device,
                                                     distributed=distributed,
                                                     rank=rank,
                                                     settings=settings)

    # Load model weight from previously saved checkpoint for incremental training
    load_from_pretrained_checkpoint(settings, model_wrapper, distributed)

    num_params = sum([p.data.nelement() for p in model_wrapper.model.parameters()])
    logger.info("[model: {}, #param: {}]".format(model_wrapper.model_name, num_params))

    metrics = ClassificationMetrics(labels=dataset_wrapper.labels, multilabel=multilabel)

    # setup optimizer
    optimizer = setup_optimizer(model_wrapper.model, settings=settings)

    # check imbalance rate to enable weighted loss to mitigate class imbalance problem
    weighted_loss_factor = settings[TrainingLiterals.WEIGHTED_LOSS]
    imbalance_rate, class_weights = _compute_class_weight(dataset_wrapper, weighted_loss_factor, device=device)
    mesg = "[Input Data] class imbalance rate: {0}, weighted_loss factor: {1}" \
        .format(imbalance_rate, weighted_loss_factor)

    if (weighted_loss_factor == 1 or weighted_loss_factor == 2) and \
            imbalance_rate > settings[TrainingLiterals.IMBALANCE_RATE_THRESHOLD]:
        criterion = _get_criterion(multilabel=multilabel, class_weights=class_weights)
        mesg += ", Weighted loss is applied."
    else:
        criterion = _get_criterion(multilabel=multilabel)
        mesg += ", Weighted loss is NOT applied."
    logger.info(mesg)

    best_model_wts = copy.deepcopy(model_wrapper.state_dict())
    best_score = 0.0
    best_epoch = 0
    no_progress_counter = 0
    best_model_metrics = None

    # setup dataloader
    train_dataloader, valid_dataloader = _get_train_test_dataloaders(dataset_wrapper, valid_dataset=valid_dataset,
                                                                     valid_resize_size=model_wrapper.valid_resize_size,
                                                                     valid_crop_size=model_wrapper.valid_crop_size,
                                                                     train_crop_size=model_wrapper.train_crop_size,
                                                                     train_transforms=train_transforms,
                                                                     valid_transforms=valid_transforms,
                                                                     batch_size=training_batch_size,
                                                                     validation_batch_size=validation_batch_size,
                                                                     num_workers=num_workers,
                                                                     distributed=distributed)

    logger.info("[start training: "
                "train batch_size: {}, val batch_size: {}]".format(training_batch_size, validation_batch_size))

    # setup lr_scheduler
    lr_scheduler = setup_lr_scheduler(optimizer, batches_per_epoch=len(train_dataloader), settings=settings)

    primary_metric_supported = metrics.metric_supported(primary_metric)
    backup_primary_metric = MetricsLiterals.ACCURACY  # Accuracy is always supported.
    if not primary_metric_supported:
        logger.warning("Given primary metric {} is not supported. "
                       "Reporting {} values as {} values.".format(primary_metric,
                                                                  backup_primary_metric, primary_metric))

    epoch_time = AverageMeter()
    epoch_end = time.time()
    train_start = time.time()
    train_sys_meter = SystemMeter()
    valid_sys_meter = SystemMeter()
    specs = {
        'multilabel': model_wrapper.multilabel,
        'model_settings': model_wrapper.model_settings,
        'labels': dataset_wrapper.labels
    }
    for epoch in range(number_of_epochs):

        if distributed:
            if train_dataloader.distributed_sampler is None:
                msg = "train_dataloader.distributed_sampler is None in distributed mode. " \
                      "Cannot shuffle data after each epoch."
                logger.error(msg)
                raise AutoMLVisionSystemException(msg, has_pii=False)
            train_dataloader.distributed_sampler.set_epoch(epoch)

        epoch_train_loss = train_one_epoch(model_wrapper, epoch=epoch, dataloader=train_dataloader,
                                           criterion=criterion, optimizer=optimizer, device=device,
                                           lr_scheduler=lr_scheduler, multilabel=multilabel,
                                           system_meter=train_sys_meter, distributed=distributed, metrics=metrics,
                                           grad_accum_steps=grad_accum_steps, grad_clip_type=grad_clip_type)

        computed_train_metrics = metrics.compute(is_train=True)
        computed_train_metrics[MetricsLiterals.AUTOML_CLASSIFICATION_TRAIN_METRICS][
            scoring_constants.LOG_LOSS] = epoch_train_loss

        # save model checkpoint
        if checkpoint_freq is not None and epoch % checkpoint_freq == 0 and master_process:

            save_model_checkpoint(epoch=epoch,
                                  model_name=model_name,
                                  number_of_classes=model_wrapper.number_of_classes,
                                  specs=specs,
                                  model_state=model_wrapper.state_dict(),
                                  optimizer_state=optimizer.state_dict(),
                                  lr_scheduler_state=lr_scheduler.lr_scheduler.state_dict(),
                                  output_dir=output_dir,
                                  model_file_name_prefix=str(epoch) + '_')

        final_epoch = epoch + 1 == number_of_epochs
        if epoch % eval_freq == 0 or final_epoch:
            is_best = False
            epoch_val_loss = validate(model_wrapper, epoch=epoch, dataloader=valid_dataloader,
                                      criterion=_get_criterion(multilabel=multilabel),
                                      metrics=metrics, device=device, multilabel=multilabel,
                                      system_meter=valid_sys_meter, distributed=distributed)

            computed_metrics = metrics.compute(is_train=False)
            computed_metrics[MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS][
                scoring_constants.LOG_LOSS] = epoch_val_loss

            if not primary_metric_supported:
                computed_metrics[MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS][primary_metric] = \
                    computed_metrics[MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS][backup_primary_metric]

            # start incrementing no progress counter only after early_stopping_delay
            if epoch >= early_stopping_delay:
                no_progress_counter += 1

            if computed_metrics[MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS][primary_metric] > best_score:
                no_progress_counter = 0

            if computed_metrics[MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS][primary_metric] >= best_score:
                best_model_metrics = computed_metrics
                is_best = True
                best_epoch = epoch
                best_score = computed_metrics[MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS][primary_metric]

            # save best model checkpoint
            if is_best and master_process:
                best_model_wts = copy.deepcopy(model_wrapper.state_dict())
                save_model_checkpoint(epoch=best_epoch,
                                      model_name=model_name,
                                      number_of_classes=model_wrapper.number_of_classes,
                                      specs=specs,
                                      model_state=best_model_wts,
                                      optimizer_state=optimizer.state_dict(),
                                      lr_scheduler_state=lr_scheduler.lr_scheduler.state_dict(),
                                      output_dir=output_dir)

            logger.info("Current best primary metric score: {0:.3f} (at epoch {1})".format(best_score, best_epoch))

        # log to Run History every epoch with previously computed metrics, if not computed in the current epoch
        # to sync the metrics reported index with actual training epoch.
        if master_process and azureml_run is not None:
            log_classification_metrics(metrics, computed_train_metrics, primary_metric, azureml_run)
            log_classification_metrics(metrics, computed_metrics, primary_metric, azureml_run,
                                       final_epoch=final_epoch, best_model_metrics=best_model_metrics)

        # measure elapsed time
        epoch_time.update(time.time() - epoch_end)
        epoch_end = time.time()
        mesg = "Epoch-level: [{0}]\t" \
               "Epoch-level Time {epoch_time.value:.4f} " \
               "(avg {epoch_time.avg:.4f})".format(epoch, epoch_time=epoch_time)
        logger.info(mesg)

        if is_enabled_early_stopping and no_progress_counter >= early_stopping_patience:
            logger.info("No progress registered after {0} epochs. "
                        "Early stopping the run.".format(no_progress_counter))

            # In-case of early stopping the final_epoch is passed as true to allow logging
            # the best model metrics till that epoch.
            if master_process and azureml_run is not None:
                # condition to prevent metrics being logged again when early stopping happens at the final epoch
                if not final_epoch:
                    log_classification_metrics(metrics, computed_metrics, primary_metric, azureml_run,
                                               final_epoch=True, best_model_metrics=best_model_metrics)
            break

        # collect garbage after each epoch
        gc.collect()

    # measure total training time
    train_time = time.time() - train_start
    common_utils.log_end_training_stats(train_time, epoch_time, train_sys_meter, valid_sys_meter)

    if master_process:
        logger.info("Writing scoring and featurization scripts.")
        write_scoring_script(output_dir)

        write_artifacts(model_wrapper=model_wrapper,
                        best_model_weights=best_model_wts,
                        labels=dataset_wrapper.labels,
                        output_dir=output_dir,
                        run=azureml_run,
                        best_metric=best_score,
                        task_type=task_type,
                        device=device,
                        enable_onnx_norm=enable_onnx_norm,
                        model_settings=model_wrapper.model_settings,
                        save_as_mlflow=save_as_mlflow)

    if log_verbose_metrics:
        common_utils.log_verbose_metrics_to_rh(train_time, epoch_time, train_sys_meter, valid_sys_meter, azureml_run)

    return model_wrapper.model_settings
