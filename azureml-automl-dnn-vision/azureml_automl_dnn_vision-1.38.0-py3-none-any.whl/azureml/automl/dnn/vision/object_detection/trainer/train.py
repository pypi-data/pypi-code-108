# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Classes that wrap training steps"""
import copy
import gc
import itertools
import time
import torch
from typing import Any, cast, Dict, List
from azureml.automl.dnn.vision.common import distributed_utils, utils
from azureml.automl.dnn.vision.common.artifacts_utils import save_model_checkpoint, write_artifacts
from azureml.automl.dnn.vision.common.average_meter import AverageMeter
from azureml.automl.dnn.vision.common.constants import SettingsLiterals as CommonSettingsLiterals, \
    TrainingCommonSettings, TrainingLiterals as CommonTrainingLiterals
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionSystemException
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.system_meter import SystemMeter
from azureml.automl.dnn.vision.common.trainer.lrschedule import LRSchedulerUpdateType
from azureml.automl.dnn.vision.object_detection.common import boundingbox, masktools
from azureml.automl.dnn.vision.object_detection.common.constants import ValidationMetricType, \
    TrainingLiterals, TilingLiterals
from azureml.automl.dnn.vision.object_detection.common.object_detection_utils import compute_metrics, \
    write_per_label_metrics_file
from azureml.automl.dnn.vision.object_detection.common.tiling_helper import \
    merge_predictions_from_tiles_and_images
from azureml.automl.dnn.vision.object_detection.data.dataset_wrappers import DatasetProcessingType
from azureml.automl.dnn.vision.object_detection.eval import cocotools
from azureml.automl.dnn.vision.object_detection.eval.utils import prepare_bounding_boxes_for_eval
from azureml.automl.dnn.vision.object_detection.eval.vocmap import VocMap
from azureml.automl.dnn.vision.object_detection.writers.score_script_utils import write_scoring_script
from contextlib import nullcontext
from torch.tensor import Tensor


logger = get_logger(__name__)


def move_images_to_device(images: List[Tensor], device: torch.device) -> List[Tensor]:
    """Convenience function to move images to device (gpu/cpu).

    :param images: Batch of images
    :type images: Pytorch tensor
    :param device: Target device
    :type device: torch.device
    :return: Batch of images moved to the device
    :rtype: List[Tensor]
    """

    return [image.to(device) for image in images]


def move_targets_to_device(targets, device: torch.device):
    """Convenience function to move training targets to device (gpu/cpu)

    :param targets: Batch Training targets (bounding boxes and classes)
    :type targets: Dictionary
    :param device: Target device
    :type device: torch.device
    """

    return [{k: v.to(device) for k, v in target.items()} for
            target in targets]


def train_one_epoch(model, optimizer, scheduler, train_data_loader,
                    device, criterion, epoch, print_freq, system_meter, distributed, grad_accum_steps,
                    grad_clip_type: str):
    """Train a model for one epoch

    :param model: Model to be trained
    :type model: Pytorch nn.Module
    :param optimizer: Optimizer used in training
    :type optimizer: Pytorch optimizer
    :param scheduler: Learning Rate Scheduler wrapper
    :type scheduler: BaseLRSchedulerWrapper (see common.trainer.lrschedule)
    :param train_data_loader: Data loader for training data
    :type train_data_loader: Pytorch data loader
    :param device: Target device
    :type device: Pytorch device
    :param criterion: Loss function wrapper
    :type criterion: Object derived from BaseCriterionWrapper (see object_detection.train.criterion)
    :param epoch: Current training epoch
    :type epoch: int
    :param print_freq: How often you want to print the output
    :type print_freq: int
    :param system_meter: A SystemMeter to collect system properties
    :type system_meter: SystemMeter
    :param distributed: Training in distributed mode or not
    :type distributed: bool
    :param grad_accum_steps: gradient accumulation steps which is used to accumulate the gradients of those steps
     without updating model variables/weights
    :type grad_accum_steps: int
    :param clip_type: The type of gradient clipping. See GradClipType
    :type grad_clip_type: str
    """

    batch_time = AverageMeter()
    data_time = AverageMeter()
    losses = AverageMeter()

    model.train()

    # grad_accum_steps should be positive, smaller or equal than the number of batches per epoch
    grad_accum_steps = min(len(train_data_loader), max(grad_accum_steps, 1))
    logger.info("[grad_accumulation_step: {}]".format(grad_accum_steps))
    optimizer.zero_grad()

    end = time.time()
    uneven_batches_context_manager = model.join() if distributed else nullcontext()

    with uneven_batches_context_manager:
        for i, (images, targets, info) in enumerate(utils._data_exception_safe_iterator(iter(train_data_loader))):
            # measure data loading time
            data_time.update(time.time() - end)

            images = move_images_to_device(images, device)
            targets = move_targets_to_device(targets, device)

            loss_dict = criterion.evaluate(model, images, targets)
            loss = sum(loss_dict.values())
            loss /= grad_accum_steps
            loss = cast(Tensor, loss)
            loss_value = loss.item()
            # raise an UserException if loss is too big
            utils.check_loss_explosion(loss_value)
            loss.backward()

            if (i + 1) % grad_accum_steps == 0 or i == len(train_data_loader) - 1:
                # gradient clipping
                utils.clip_gradient(model.parameters(), grad_clip_type)
                optimizer.step()
                optimizer.zero_grad()

            if scheduler.update_type == LRSchedulerUpdateType.BATCH:
                scheduler.lr_scheduler.step()

            # record loss and measure elapsed time
            losses.update(loss_value, len(images))
            batch_time.update(time.time() - end)
            end = time.time()

            # delete tensors which have a valid grad_fn
            del loss, loss_dict

            if i % print_freq == 0 or i == len(train_data_loader) - 1:
                mesg = "Epoch: [{0}][{1}/{2}]\t" "lr: {3}\t" "Time {batch_time.value:.4f} ({batch_time.avg:.4f})\t"\
                       "Data {data_time.value:.4f} ({data_time.avg:.4f})\t" "Loss {loss.value:.4f} " \
                       "({loss.avg:.4f})".format(epoch, i, len(train_data_loader), optimizer.param_groups[0]["lr"],
                                                 batch_time=batch_time, data_time=data_time, loss=losses)
                logger.info(mesg)

                system_meter.log_system_stats()

    if scheduler.update_type == LRSchedulerUpdateType.EPOCH:
        scheduler.lr_scheduler.step()


def validate(model, val_data_loader, device, val_index_map, system_meter, distributed,
             tile_predictions_nms_thresh, tiling_merge_predictions_time, tiling_nms_time):
    """Gets model results on validation set.

    :param model: Model to score
    :type model: Pytorch nn.Module
    :param val_data_loader: Data loader for validation data
    :type val_data_loader: Pytorch Data Loader
    :param device: Target device
    :type device: Pytorch device
    :param val_index_map: Map from numerical indices to class names
    :type val_index_map: List of strings
    :returns: List of detections
    :rtype: List of ImageBoxes (see object_detection.common.boundingbox)
    :param system_meter: A SystemMeter to collect system properties
    :type system_meter: SystemMeter
    :param distributed: Training in distributed mode or not
    :type distributed: bool
    :param tile_predictions_nms_thresh: The iou threshold to use to perform nms while merging predictions in tiling.
    :type tile_predictions_nms_thresh: float
    :param tiling_merge_predictions_time: Meter to record predictions merging time in tiling.
    :type tiling_merge_predictions_time: AverageMeter
    :param tiling_nms_time: Meter to record nms time when merging predictions in tiling.
    :type tiling_nms_time: AverageMeter
    :return: Detections in format that can be consumed by cocotools/vocmap
    :rtype: List of dicts
    """

    batch_time = AverageMeter()

    model.eval()

    bounding_boxes = []
    label_with_info_list = []
    end = time.time()
    with torch.no_grad():
        for i, (images, targets, infos) in enumerate(utils._data_exception_safe_iterator(iter(val_data_loader))):
            images = move_images_to_device(images, device)

            # We have observed that pytorch DDP does some AllReduce calls during eval model as well.
            # When there are uneven number of batches across worker processes, there is issue with mismatch
            # of distributed calls between processes and it leads to blocked processes and hangs.
            # Using the pytorch model instead of DDP model to run validation to avoid sync calls during eval.
            # One other observation is that AllReduce calls from DDP are only seen when we use .join() during
            # training phase.
            base_torch_model = model.module if distributed else model
            labels = base_torch_model(images)

            for info, label in zip(infos, labels):
                label_with_info = {}
                label_with_info.update(info)
                label_with_info.update(label)

                # move predicted labels to cpu to save gpu memory
                label_with_info["boxes"] = label_with_info["boxes"].cpu()
                label_with_info["labels"] = label_with_info["labels"].cpu()
                label_with_info["scores"] = label_with_info["scores"].cpu()

                # encode masks as rle to save memory
                masks = label_with_info.get("masks", None)
                if masks is not None:
                    masks = masks.cpu()
                    masks = (masks > 0.5)
                    rle_masks = []
                    for mask in masks:
                        rle = masktools.encode_mask_as_rle(mask)
                        rle_masks.append(rle)
                    label_with_info["masks"] = rle_masks

                label_with_info_list.append(label_with_info)

            # measure elapsed time
            batch_time.update(time.time() - end)
            end = time.time()

            if i % 100 == 0 or i == len(val_data_loader) - 1:
                mesg = "Test: [{0}/{1}]\t" \
                       "Time {batch_time.value:.4f} ({batch_time.avg:.4f})".format(i, len(val_data_loader),
                                                                                   batch_time=batch_time)
                logger.info(mesg)

                system_meter.log_system_stats()

        if val_data_loader.dataset.dataset_processing_type == DatasetProcessingType.IMAGES_AND_TILES:
            merged_label_with_info_list = merge_predictions_from_tiles_and_images(
                label_with_info_list=label_with_info_list, nms_thresh=tile_predictions_nms_thresh,
                device="cpu", merge_predictions_time=tiling_merge_predictions_time, nms_time=tiling_nms_time)
        else:
            merged_label_with_info_list = label_with_info_list

        for label_with_info in merged_label_with_info_list:
            image_boxes = boundingbox.ImageBoxes(label_with_info["filename"], val_index_map)
            image_boxes.add_boxes(label_with_info["boxes"],
                                  label_with_info["labels"],
                                  label_with_info["scores"],
                                  label_with_info.get("masks", None))
            bounding_boxes.append(image_boxes)

    eval_bounding_boxes = prepare_bounding_boxes_for_eval(bounding_boxes)

    if distributed:
        # Gather eval bounding boxes from all processes.
        eval_bounding_boxes_list = distributed_utils.all_gather(eval_bounding_boxes)
        eval_bounding_boxes = list(itertools.chain.from_iterable(eval_bounding_boxes_list))

        logger.info("Gathered {} eval bounding boxes from all processes.".format(len(eval_bounding_boxes)))

    return eval_bounding_boxes


def train(model, optimizer, scheduler, train_data_loader, val_data_loader,
          criterion, device, settings, output_dir=None, azureml_run=None):
    """Train a model

    :param model: Model to train
    :type model: Object derived from BaseObjectDetectionModelWrapper (see object_detection.models.base_model_wrapper)
    :param optimizer: Model Optimizer
    :type optimizer: Pytorch Optimizer
    :param scheduler: Learning Rate Scheduler wrapper.
    :type scheduler: BaseLRSchedulerWrapper (see common.trainer.lrschedule)
    :param train_data_loader: Data loader with training data
    :type train_data_loader: Pytorch data loader
    :param val_data_loader: Data loader with validation data.
    :type val_data_loader: Pytorch data loader
    :param criterion: Loss function
    :type criterion: Object derived from CommonCriterionWrapper (see object_detection.train.criterion)
    :param device: Target device (gpu/cpu)
    :type device: Pytorch Device
    :param settings: dictionary containing settings for training
    :type settings: dict
    :param output_dir: Output directory to write checkpoints to
    :type output_dir: str
    :param azureml_run: azureml run object
    :type azureml_run: azureml.core.run.Run
    :returns: Trained model
    :rtype: Object derived from CommonObjectDetectionModelWrapper
    """

    epoch_time = AverageMeter()

    # Extract relevant parameters from training settings
    task_type = settings[CommonSettingsLiterals.TASK_TYPE]
    primary_metric = settings[CommonTrainingLiterals.PRIMARY_METRIC]
    val_index_map = model.classes
    val_metric_type = settings[TrainingLiterals.VALIDATION_METRIC_TYPE]
    number_of_epochs = settings[CommonTrainingLiterals.NUMBER_OF_EPOCHS]
    enable_onnx_norm = settings[CommonSettingsLiterals.ENABLE_ONNX_NORMALIZATION]
    log_verbose_metrics = settings.get(CommonSettingsLiterals.LOG_VERBOSE_METRICS, False)
    is_enabled_early_stopping = settings[CommonTrainingLiterals.EARLY_STOPPING]
    early_stopping_patience = settings[CommonTrainingLiterals.EARLY_STOPPING_PATIENCE]
    early_stopping_delay = settings[CommonTrainingLiterals.EARLY_STOPPING_DELAY]
    eval_freq = settings[CommonTrainingLiterals.EVALUATION_FREQUENCY]
    checkpoint_freq = settings.get(CommonTrainingLiterals.CHECKPOINT_FREQUENCY, None)
    grad_accum_steps = settings[CommonTrainingLiterals.GRAD_ACCUMULATION_STEP]
    grad_clip_type = settings[CommonTrainingLiterals.GRAD_CLIP_TYPE]
    tile_predictions_nms_thresh = settings[TilingLiterals.TILE_PREDICTIONS_NMS_THRESH]
    save_as_mlflow = settings[CommonSettingsLiterals.SAVE_MLFLOW]

    base_model = model.model

    distributed = distributed_utils.dist_available_and_initialized()
    master_process = distributed_utils.master_process()

    best_model_wts = copy.deepcopy(model.state_dict())
    best_score = 0.0
    best_epoch = 0
    no_progress_counter = 0

    # Setup evaluation tools
    val_coco_index = None
    val_vocmap = None
    if val_metric_type in ValidationMetricType.ALL_COCO:
        val_coco_index = cocotools.create_coco_index(val_data_loader.dataset)
    if val_metric_type in ValidationMetricType.ALL_VOC:
        val_vocmap = VocMap(val_data_loader.dataset)

    computed_metrics: Dict[str, Any] = {}
    per_label_metrics: Dict[str, Any] = {}

    epoch_end = time.time()
    train_start = time.time()
    coco_metric_time = AverageMeter()
    voc_metric_time = AverageMeter()
    train_sys_meter = SystemMeter()
    valid_sys_meter = SystemMeter()
    tiling_merge_predictions_time = AverageMeter()
    tiling_nms_time = AverageMeter()

    specs = {
        'model_specs': model.specs,
        'model_settings': model.model_settings.get_settings_dict(),
        'classes': model.classes,
        'inference_settings': model.inference_settings
    }

    for epoch in range(number_of_epochs):
        logger.info("Training epoch {}.".format(epoch))

        if distributed:
            if train_data_loader.distributed_sampler is None:
                msg = "train_data_loader.distributed_sampler is None in distributed mode. " \
                      "Cannot shuffle data after each epoch."
                logger.error(msg)
                raise AutoMLVisionSystemException(msg, has_pii=False)
            train_data_loader.distributed_sampler.set_epoch(epoch)

        train_one_epoch(base_model, optimizer, scheduler,
                        train_data_loader, device, criterion, epoch,
                        print_freq=100, system_meter=train_sys_meter, distributed=distributed,
                        grad_accum_steps=grad_accum_steps, grad_clip_type=grad_clip_type)

        # save model checkpoint
        if checkpoint_freq is not None and epoch % checkpoint_freq == 0 and master_process:
            save_model_checkpoint(epoch=epoch,
                                  model_name=model.model_name,
                                  number_of_classes=model.number_of_classes,
                                  specs=specs,
                                  model_state=model.state_dict(),
                                  optimizer_state=optimizer.state_dict(),
                                  lr_scheduler_state=scheduler.lr_scheduler.state_dict(),
                                  output_dir=output_dir,
                                  model_file_name_prefix=str(epoch) + '_')

        final_epoch = epoch + 1 == number_of_epochs
        if epoch % eval_freq == 0 or final_epoch:
            eval_bounding_boxes = validate(model=base_model, val_data_loader=val_data_loader, device=device,
                                           val_index_map=val_index_map, system_meter=valid_sys_meter,
                                           distributed=distributed,
                                           tile_predictions_nms_thresh=tile_predictions_nms_thresh,
                                           tiling_merge_predictions_time=tiling_merge_predictions_time,
                                           tiling_nms_time=tiling_nms_time)

            if not eval_bounding_boxes:
                logger.info("no detected bboxes for evaluation")

            is_best = False
            if val_metric_type != ValidationMetricType.NONE:
                map_score = compute_metrics(eval_bounding_boxes, val_metric_type,
                                            val_coco_index, val_vocmap, computed_metrics, per_label_metrics,
                                            coco_metric_time, voc_metric_time, primary_metric)

                # start incrementing no progress counter only after early_stopping_delay
                if epoch >= early_stopping_delay:
                    no_progress_counter += 1

                if map_score > best_score:
                    no_progress_counter = 0

                if map_score >= best_score:
                    is_best = True
                    best_epoch = epoch
                    best_score = map_score
            else:
                logger.info("val_metric_type is None. Not computing metrics.")
                is_best = True
                best_epoch = epoch

            # save best model checkpoint
            if is_best and master_process:
                best_model_wts = copy.deepcopy(model.state_dict())
                save_model_checkpoint(epoch=best_epoch,
                                      model_name=model.model_name,
                                      number_of_classes=model.number_of_classes,
                                      specs=specs,
                                      model_state=best_model_wts,
                                      optimizer_state=optimizer.state_dict(),
                                      lr_scheduler_state=scheduler.lr_scheduler.state_dict(),
                                      output_dir=output_dir)

            logger.info("Current best primary metric score: {0:.3f} (at epoch {1})".format(round(best_score, 5),
                                                                                           best_epoch))

        # log to Run History every epoch with previously computed metrics, if not computed in the current epoch
        # to sync the metrics reported index with actual training epoch.
        if master_process and azureml_run is not None:
            utils.log_all_metrics(computed_metrics, azureml_run=azureml_run, add_to_logger=True)

        # measure elapsed time
        epoch_time.update(time.time() - epoch_end)
        epoch_end = time.time()
        msg = "Epoch-level: [{0}]\t" \
              "Epoch-level Time {epoch_time.value:.4f} ({epoch_time.avg:.4f})".format(epoch, epoch_time=epoch_time)
        logger.info(msg)

        if is_enabled_early_stopping and no_progress_counter > early_stopping_patience:
            logger.info("No progress registered after {0} epochs. "
                        "Early stopping the run.".format(no_progress_counter))
            break

        # collect garbage after each epoch
        gc.collect()

    # measure total training time
    train_time = time.time() - train_start
    utils.log_end_training_stats(train_time, epoch_time, train_sys_meter, valid_sys_meter)

    if log_verbose_metrics:
        utils.log_verbose_metrics_to_rh(train_time, epoch_time, train_sys_meter, valid_sys_meter, azureml_run)

    if master_process:
        write_scoring_script(output_dir, task_type=task_type)

        write_per_label_metrics_file(output_dir, per_label_metrics, val_index_map)

        model_settings = {} if model.model_settings is None else model.model_settings.get_settings_dict()

        write_artifacts(model_wrapper=model,
                        best_model_weights=best_model_wts,
                        labels=model.classes,
                        output_dir=output_dir,
                        run=azureml_run,
                        best_metric=best_score,
                        task_type=task_type,
                        device=device,
                        enable_onnx_norm=enable_onnx_norm,
                        model_settings=model_settings,
                        save_as_mlflow=save_as_mlflow
                        )
