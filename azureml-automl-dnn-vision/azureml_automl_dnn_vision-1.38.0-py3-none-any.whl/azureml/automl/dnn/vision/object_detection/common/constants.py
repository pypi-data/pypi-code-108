# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines literals and constants for the object detection part of the package."""

from azureml.automl.dnn.vision.common.constants import (
    ArtifactLiterals, CommonSettings, DistributedLiterals, DistributedParameters, MetricsLiterals,
    SettingsLiterals as CommonSettingsLiterals, ScoringLiterals as CommonScoringLiterals,
    TrainingCommonSettings, TrainingLiterals as CommonTrainingLiterals,
    safe_to_log_vision_common_settings, safe_to_log_automl_settings
)


class CriterionNames:
    """String names for different loss functions."""
    LOSS_FROM_MODEL = "LOSS_FROM_MODEL"


class DataLoaderParameterLiterals:
    """String names for dataloader parameters."""
    BATCH_SIZE = "batch_size"
    SHUFFLE = "shuffle"
    NUM_WORKERS = "num_workers"
    DISTRIBUTED = "distributed"
    DROP_LAST = "drop_last"


class DataLoaderParameters:
    """Default parameters for dataloaders."""
    DEFAULT_BATCH_SIZE = 4
    DEFAULT_SHUFFLE = True
    DEFAULT_NUM_WORKERS = None
    DEFAULT_DISTRIBUTED = False
    DEFAULT_DROP_LAST = False


class DatasetFieldLabels:
    """Keys for input datasets."""
    X_0_PERCENT = "topX"
    Y_0_PERCENT = "topY"
    X_1_PERCENT = "bottomX"
    Y_1_PERCENT = "bottomY"
    IS_CROWD = "isCrowd"
    IMAGE_URL = "imageUrl"
    IMAGE_DETAILS = "imageDetails"
    IMAGE_LABEL = "label"
    CLASS_LABEL = "label"
    WIDTH = "width"
    HEIGHT = "height"
    POLYGON = "polygon"


class ModelNames:
    """String names for models."""
    FASTER_RCNN_RESNET152_FPN = "fasterrcnn_resnet152_fpn"
    FASTER_RCNN_RESNET101_FPN = "fasterrcnn_resnet101_fpn"
    FASTER_RCNN_RESNET50_FPN = "fasterrcnn_resnet50_fpn"
    FASTER_RCNN_RESNET34_FPN = "fasterrcnn_resnet34_fpn"
    FASTER_RCNN_RESNET18_FPN = "fasterrcnn_resnet18_fpn"
    MASK_RCNN_RESNET152_FPN = "maskrcnn_resnet152_fpn"
    MASK_RCNN_RESNET101_FPN = "maskrcnn_resnet101_fpn"
    MASK_RCNN_RESNET50_FPN = "maskrcnn_resnet50_fpn"
    MASK_RCNN_RESNET34_FPN = "maskrcnn_resnet34_fpn"
    MASK_RCNN_RESNET18_FPN = "maskrcnn_resnet18_fpn"
    YOLO_V5 = "yolov5"
    RETINANET_RESNET50_FPN = "retinanet_resnet50_fpn"


class OutputFields:
    """Keys for the outputs of the object detection network."""
    BOXES_LABEL = "boxes"
    CLASSES_LABEL = "labels"
    SCORES_LABEL = "scores"
    VOCMAP_RESULT = "vocmap_result"


class ValidationMetricType:
    """ Metric computation method to use for validation metrics."""
    NONE = "none"
    COCO = "coco"
    VOC = "voc"
    COCO_VOC = "coco_voc"

    ALL_COCO = [COCO, COCO_VOC]
    ALL_VOC = [VOC, COCO_VOC]
    ALL_TYPES = [NONE, COCO, VOC, COCO_VOC]


class TrainingLiterals:
    """String keys for training parameters."""
    VALIDATION_METRIC_TYPE = "validation_metric_type"


class PredictionLiterals:
    """Strings that will be keys in the output json during prediction."""
    BOX = 'box'
    BOXES = 'boxes'
    FILENAME = 'filename'
    LABEL = 'label'
    POLYGON = 'polygon'
    SCORE = 'score'


class TilingLiterals:
    """String keys for tiling parameters."""
    TILE_GRID_SIZE = "tile_grid_size"
    TILE_OVERLAP_RATIO = "tile_overlap_ratio"
    TILE_PREDICTIONS_NMS_THRESH = "tile_predictions_nms_thresh"


class TilingParameters:
    """Defaults for tiling paramters."""
    DEFAULT_TILE_OVERLAP_RATIO = 0.25
    DEFAULT_TILE_PREDICTIONS_NMS_THRESH = 0.25


training_settings_defaults = {
    CommonSettingsLiterals.DEVICE: CommonSettings.DEVICE,
    CommonSettingsLiterals.DATA_FOLDER: CommonSettings.DATA_FOLDER,
    CommonSettingsLiterals.LABELS_FILE_ROOT: CommonSettings.LABELS_FILE_ROOT,
    CommonTrainingLiterals.PRIMARY_METRIC: MetricsLiterals.MEAN_AVERAGE_PRECISION,
    CommonTrainingLiterals.NUMBER_OF_EPOCHS: 15,
    CommonTrainingLiterals.TRAINING_BATCH_SIZE: 2,
    CommonTrainingLiterals.VALIDATION_BATCH_SIZE: 1,
    CommonTrainingLiterals.LEARNING_RATE: 0.005,
    CommonTrainingLiterals.EARLY_STOPPING: TrainingCommonSettings.DEFAULT_EARLY_STOPPING,
    CommonTrainingLiterals.EARLY_STOPPING_PATIENCE: TrainingCommonSettings.DEFAULT_EARLY_STOPPING_PATIENCE,
    CommonTrainingLiterals.EARLY_STOPPING_DELAY: TrainingCommonSettings.DEFAULT_EARLY_STOPPING_DELAY,
    CommonTrainingLiterals.GRAD_ACCUMULATION_STEP: TrainingCommonSettings.DEFAULT_GRAD_ACCUMULATION_STEP,
    CommonTrainingLiterals.GRAD_CLIP_TYPE: TrainingCommonSettings.DEFAULT_GRAD_CLIP_TYPE,
    CommonTrainingLiterals.OPTIMIZER: TrainingCommonSettings.DEFAULT_OPTIMIZER,
    CommonTrainingLiterals.MOMENTUM: TrainingCommonSettings.DEFAULT_MOMENTUM,
    CommonTrainingLiterals.WEIGHT_DECAY: TrainingCommonSettings.DEFAULT_WEIGHT_DECAY,
    CommonTrainingLiterals.NESTEROV: TrainingCommonSettings.DEFAULT_NESTEROV,
    CommonTrainingLiterals.BETA1: TrainingCommonSettings.DEFAULT_BETA1,
    CommonTrainingLiterals.BETA2: TrainingCommonSettings.DEFAULT_BETA2,
    CommonTrainingLiterals.AMSGRAD: TrainingCommonSettings.DEFAULT_AMSGRAD,
    CommonTrainingLiterals.LR_SCHEDULER: TrainingCommonSettings.DEFAULT_LR_SCHEDULER,
    CommonTrainingLiterals.STEP_LR_GAMMA: TrainingCommonSettings.DEFAULT_STEP_LR_GAMMA,
    CommonTrainingLiterals.STEP_LR_STEP_SIZE: TrainingCommonSettings.DEFAULT_STEP_LR_STEP_SIZE,
    CommonTrainingLiterals.WARMUP_COSINE_LR_CYCLES: TrainingCommonSettings.DEFAULT_WARMUP_COSINE_LR_CYCLES,
    CommonTrainingLiterals.WARMUP_COSINE_LR_WARMUP_EPOCHS:
        TrainingCommonSettings.DEFAULT_WARMUP_COSINE_LR_WARMUP_EPOCHS,
    CommonTrainingLiterals.EVALUATION_FREQUENCY: TrainingCommonSettings.DEFAULT_EVALUATION_FREQUENCY,
    CommonTrainingLiterals.SPLIT_RATIO: TrainingCommonSettings.DEFAULT_SPLIT_RATIO,
    CommonSettingsLiterals.ENABLE_ONNX_NORMALIZATION: False,
    CommonSettingsLiterals.IGNORE_DATA_ERRORS: True,
    CommonSettingsLiterals.LOG_SCORING_FILE_INFO: False,
    CommonSettingsLiterals.NUM_WORKERS: 4,
    CommonSettingsLiterals.OUTPUT_DIR: ArtifactLiterals.OUTPUT_DIR,
    CommonSettingsLiterals.OUTPUT_SCORING: False,
    CommonSettingsLiterals.VALIDATE_SCORING: False,
    CommonSettingsLiterals.SAVE_MLFLOW: False,
    DistributedLiterals.DISTRIBUTED: DistributedParameters.DEFAULT_DISTRIBUTED,
    DistributedLiterals.MASTER_ADDR: DistributedParameters.DEFAULT_MASTER_ADDR,
    DistributedLiterals.MASTER_PORT: DistributedParameters.DEFAULT_MASTER_PORT,
    TrainingLiterals.VALIDATION_METRIC_TYPE: ValidationMetricType.VOC,
    TilingLiterals.TILE_OVERLAP_RATIO: TilingParameters.DEFAULT_TILE_OVERLAP_RATIO,
    TilingLiterals.TILE_PREDICTIONS_NMS_THRESH: TilingParameters.DEFAULT_TILE_PREDICTIONS_NMS_THRESH
}

inference_settings_defaults = {
    CommonScoringLiterals.BATCH_SIZE: 2,
    CommonSettingsLiterals.NUM_WORKERS: 4
}


class ModelLiterals:
    """String keys for model parameters."""
    MIN_SIZE = "min_size"
    MAX_SIZE = "max_size"
    BOX_SCORE_THRESH = "box_score_thresh"
    BOX_NMS_THRESH = "box_nms_thresh"
    BOX_DETECTIONS_PER_IMG = "box_detections_per_img"


class RetinaNetLiterals:
    """String keys for RetinaNet parameters."""
    MIN_SIZE = "min_size"
    MAX_SIZE = "max_size"
    SCORE_THRESH = "score_thresh"
    NMS_THRESH = "nms_thresh"
    DETECTIONS_PER_IMG = "detections_per_img"


class ModelParameters:
    """Default model parameters."""
    DEFAULT_MIN_SIZE = 600
    DEFAULT_MAX_SIZE = 1333
    DEFAULT_BOX_SCORE_THRESH = 0.3
    DEFAULT_BOX_NMS_THRESH = 0.5
    DEFAULT_BOX_DETECTIONS_PER_IMG = 100


class MaskRCNNLiterals:
    """String keys for MaskRCNN parameters."""
    MASK_PREDICTOR_HIDDEN_DIM = "mask_predictor_hidden_dim"


class MaskRCNNParameters:
    """Default MaskRCNN parameters."""
    DEFAULT_MASK_PREDICTOR_HIDDEN_DIM = 256


class MaskToolsLiterals:
    """String keys for Mask tool parameters"""
    MASK_PIXEL_SCORE_THRESHOLD = 'mask_pixel_score_threshold'
    MAX_NUMBER_OF_POLYGON_POINTS = 'max_number_of_polygon_points'


class MaskToolsParameters:
    """Default values for mask tool parameters."""
    DEFAULT_MASK_PIXEL_SCORE_THRESHOLD = 0.5
    DEFAULT_MAX_NUMBER_OF_POLYGON_POINTS = 100
    DEFAULT_MAX_NUMBER_OF_POLYGON_SIMPLIFICATIONS = 25
    DEFAULT_MASK_SAFETY_PADDING = 1
    DEFAULT_GRABCUT_MARGIN = 10
    DEFAULT_GRABCUT_MODEL_LEVELS = 65
    DEFAULT_GRABCUT_NUMBER_ITERATIONS = 5
    DEFAULT_MASK_REFINE_POINTS = 25


class MaskImageExportLiterals:
    """Settings for exporting masks as bitmap images"""
    EXPORT_AS_IMAGE = 'export_as_image'
    IMAGE_TYPE = 'image_type'  # JPG, PNG, BMP supported


class MaskImageExportParameters:
    """Default settings for mask as image export"""
    DEFAULT_EXPORT_AS_IMAGE = False
    DEFAULT_IMAGE_TYPE = 'JPG'


class PredefinedLiterals:
    """Predefined string literals"""
    BG_LABEL = "--bg--"


# not safe: 'data_folder', 'labels_file_root', 'path'
safe_to_log_vision_od_settings = {
    TrainingLiterals.VALIDATION_METRIC_TYPE,

    DistributedLiterals.DISTRIBUTED,
    DistributedLiterals.MASTER_ADDR,
    DistributedLiterals.MASTER_PORT,
    DistributedLiterals.WORLD_SIZE,

    ModelLiterals.BOX_DETECTIONS_PER_IMG,
    ModelLiterals.BOX_NMS_THRESH,
    ModelLiterals.BOX_SCORE_THRESH,
    ModelLiterals.MIN_SIZE,
    ModelLiterals.MAX_SIZE,

    MaskToolsLiterals.MASK_PIXEL_SCORE_THRESHOLD,
    MaskToolsLiterals.MAX_NUMBER_OF_POLYGON_POINTS,

    TilingLiterals.TILE_GRID_SIZE,
    TilingLiterals.TILE_OVERLAP_RATIO,
    TilingLiterals.TILE_PREDICTIONS_NMS_THRESH
}

safe_to_log_settings = \
    safe_to_log_automl_settings | \
    safe_to_log_vision_common_settings | \
    safe_to_log_vision_od_settings
