# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

""" Defines literals and constants for the object detection part of the package """

from azureml.automl.dnn.vision.common.constants import CommonSettings, DistributedLiterals, \
    MetricsLiterals, SettingsLiterals as CommonSettingsLiterals, ScoringLiterals as CommonScoringLiterals, \
    TrainingCommonSettings, TrainingLiterals as CommonTrainingLiterals, \
    safe_to_log_vision_common_settings, safe_to_log_automl_settings
from azureml.automl.dnn.vision.object_detection.common.constants import ModelNames, \
    TrainingLiterals as ODTrainingLiterals, ValidationMetricType


class ModelSize:
    """Model sizes"""
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'
    EXTRA_LARGE = 'xlarge'
    ALL_TYPES = [SMALL, MEDIUM, LARGE, EXTRA_LARGE]


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


yolo_hyp_defaults = {
    'giou': 0.05,  # giou loss gain
    'cls': 0.58,  # cls loss gain
    'cls_pw': 1.0,  # cls BCELoss positive_weight
    'obj': 1.0,  # obj loss gain (*=img_size/320 if img_size != 320)
    'obj_pw': 1.0,  # obj BCELoss positive_weight
    'anchor_t': 4.0,  # anchor-multiple threshold
    'fl_gamma': 0.0,  # focal loss gamma (efficientDet default is gamma=1.5)
    'degrees': 0.0,  # image rotation (+/- deg)
    'translate': 0.0,  # image translation (+/- fraction)
    'scale': 0.5,  # image scale (+/- gain)
    'shear': 0.0,  # image shear (+/- deg)
    'gs': 32}  # grid size


class YoloLiterals:
    """String keys for Yolov5 parameters."""
    IMG_SIZE = "img_size"
    MODEL_SIZE = 'model_size'
    MULTI_SCALE = "multi_scale"
    BOX_SCORE_THRESH = "box_score_thresh"
    BOX_IOU_THRESH = "box_iou_thresh"


class YoloParameters:
    """Default Yolov5 parameters."""
    DEFAULT_IMG_SIZE = 640
    DEFAULT_MODEL_SIZE = 'medium'
    DEFAULT_MULTI_SCALE = False
    DEFAULT_MODEL_VERSION = '5.3.0'
    DEFAULT_BOX_SCORE_THRESH = 0.1
    DEFAULT_BOX_IOU_THRESH = 0.5


training_settings_defaults = {
    CommonSettingsLiterals.DEVICE: CommonSettings.DEVICE,
    CommonSettingsLiterals.DATA_FOLDER: CommonSettings.DATA_FOLDER,
    CommonSettingsLiterals.LABELS_FILE_ROOT: CommonSettings.LABELS_FILE_ROOT,
    CommonTrainingLiterals.PRIMARY_METRIC: MetricsLiterals.MEAN_AVERAGE_PRECISION,
    CommonTrainingLiterals.NUMBER_OF_EPOCHS: 30,
    CommonTrainingLiterals.TRAINING_BATCH_SIZE: 16,
    CommonTrainingLiterals.VALIDATION_BATCH_SIZE: 16,
    CommonTrainingLiterals.LEARNING_RATE: 0.01,
    CommonTrainingLiterals.EARLY_STOPPING: TrainingCommonSettings.DEFAULT_EARLY_STOPPING,
    CommonTrainingLiterals.EARLY_STOPPING_DELAY: TrainingCommonSettings.DEFAULT_EARLY_STOPPING_DELAY,
    CommonTrainingLiterals.EARLY_STOPPING_PATIENCE: TrainingCommonSettings.DEFAULT_EARLY_STOPPING_PATIENCE,
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
    CommonSettingsLiterals.MODEL_NAME: ModelNames.YOLO_V5,
    CommonSettingsLiterals.NUM_WORKERS: 8,
    CommonSettingsLiterals.OUTPUT_SCORING: False,
    CommonSettingsLiterals.VALIDATE_SCORING: False,
    CommonSettingsLiterals.SAVE_MLFLOW: False,
    ODTrainingLiterals.VALIDATION_METRIC_TYPE: ValidationMetricType.VOC,
}

inference_settings_defaults = {
    CommonScoringLiterals.BATCH_SIZE: 16,
    CommonSettingsLiterals.NUM_WORKERS: 8,
}

# not safe: 'data_folder', 'labels_file_root', 'path'
safe_to_log_vision_yolo_settings = {
    ODTrainingLiterals.VALIDATION_METRIC_TYPE,

    DistributedLiterals.DISTRIBUTED,

    YoloLiterals.IMG_SIZE,
    YoloLiterals.MODEL_SIZE,
    YoloLiterals.MULTI_SCALE,
    YoloLiterals.BOX_SCORE_THRESH,
    YoloLiterals.BOX_IOU_THRESH
}

safe_to_log_settings = \
    safe_to_log_automl_settings | \
    safe_to_log_vision_common_settings | \
    safe_to_log_vision_yolo_settings
