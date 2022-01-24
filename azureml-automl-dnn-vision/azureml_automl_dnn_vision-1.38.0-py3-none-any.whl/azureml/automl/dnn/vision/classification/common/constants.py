# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines literals and constants for the classification part of the package."""

from azureml.automl.dnn.vision.common.constants import (
    ArtifactLiterals, CommonSettings, DistributedLiterals, DistributedParameters, MetricsLiterals,
    SettingsLiterals as CommonSettingsLiterals, ScoringLiterals as CommonScoringLiterals,
    TrainingCommonSettings, TrainingLiterals as CommonTrainingLiterals,
    safe_to_log_vision_common_settings, safe_to_log_automl_settings
)


class PackageInfo:
    """Contains package details."""
    PYTHON_VERSION = '3.6'
    CONDA_PACKAGE_NAMES = ['pip']
    PIP_PACKAGE_NAMES = ['azureml-automl-dnn-vision']


class PredictionLiterals:
    """Strings that will be keys in the output json during prediction."""
    FEATURE_VECTOR = 'feature_vector'
    FILENAME = 'filename'
    LABELS = 'labels'
    PROBS = 'probs'


class LoggingLiterals:
    """Literals that help logging and correlating different training runs."""
    PROJECT_ID = 'project_id'
    VERSION_NUMBER = 'version_number'
    TASK_TYPE = 'task_type'


class TrainingLiterals:
    """String keys for training parameters."""
    # Report detailed metrics like per class/sample f1, f2, precision, recall scores.
    DETAILED_METRICS = 'detailed_metrics'
    # data imbalance ratio (#data from largest class /#data from smallest class)
    IMBALANCE_RATE_THRESHOLD = "imbalance_rate_threshold"
    # applying class-level weighting in weighted loss for class imbalance
    WEIGHTED_LOSS = "weighted_loss"


class ModelNames:
    """Currently supported model names."""
    RESNET18 = 'resnet18'
    RESNET34 = 'resnet34'
    RESNET50 = 'resnet50'
    RESNET101 = 'resnet101'
    RESNET152 = 'resnet152'
    RESNEST50 = 'resnest50'
    RESNEST101 = 'resnest101'
    MOBILENETV2 = 'mobilenetv2'
    SERESNEXT = 'seresnext'
    VITB16R224 = 'vitb16r224'
    VITS16R224 = 'vits16r224'
    VITL16R224 = 'vitl16r224'


class ModelLiterals:
    """String keys for model parameters."""
    RESIZE_SIZE = "resize_size"
    CROP_SIZE = "crop_size"
    VALID_RESIZE_SIZE = "valid_resize_size"
    VALID_CROP_SIZE = "valid_crop_size"
    TRAIN_CROP_SIZE = "train_crop_size"


class ModelParameters:
    """Default model parameters."""
    DEFAULT_VALID_RESIZE_SIZE = 256
    DEFAULT_VALID_CROP_SIZE = 224
    DEFAULT_TRAIN_CROP_SIZE = 224
    DEFAULT_IMAGE_MEAN = [0.485, 0.456, 0.406]
    DEFAULT_IMAGE_STD = [0.229, 0.224, 0.225]


base_training_settings_defaults = {
    CommonSettingsLiterals.DEVICE: CommonSettings.DEVICE,
    CommonSettingsLiterals.DATA_FOLDER: CommonSettings.DATA_FOLDER,
    CommonSettingsLiterals.LABELS_FILE_ROOT: CommonSettings.LABELS_FILE_ROOT,
    CommonTrainingLiterals.NUMBER_OF_EPOCHS: 15,
    CommonTrainingLiterals.TRAINING_BATCH_SIZE: 78,
    CommonTrainingLiterals.VALIDATION_BATCH_SIZE: 78,
    CommonTrainingLiterals.EARLY_STOPPING: TrainingCommonSettings.DEFAULT_EARLY_STOPPING,
    CommonTrainingLiterals.EARLY_STOPPING_PATIENCE: TrainingCommonSettings.DEFAULT_EARLY_STOPPING_PATIENCE,
    CommonTrainingLiterals.EARLY_STOPPING_DELAY: TrainingCommonSettings.DEFAULT_EARLY_STOPPING_DELAY,
    CommonTrainingLiterals.GRAD_ACCUMULATION_STEP: TrainingCommonSettings.DEFAULT_GRAD_ACCUMULATION_STEP,
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
    CommonTrainingLiterals.GRAD_CLIP_TYPE: TrainingCommonSettings.DEFAULT_GRAD_CLIP_TYPE,
    CommonTrainingLiterals.EVALUATION_FREQUENCY: TrainingCommonSettings.DEFAULT_EVALUATION_FREQUENCY,
    CommonTrainingLiterals.SPLIT_RATIO: TrainingCommonSettings.DEFAULT_SPLIT_RATIO,
    CommonSettingsLiterals.ENABLE_ONNX_NORMALIZATION: False,
    CommonSettingsLiterals.IGNORE_DATA_ERRORS: True,
    CommonSettingsLiterals.LOG_SCORING_FILE_INFO: False,
    CommonSettingsLiterals.MULTILABEL: False,
    CommonSettingsLiterals.NUM_WORKERS: 8,
    CommonSettingsLiterals.OUTPUT_DIR: ArtifactLiterals.OUTPUT_DIR,
    CommonSettingsLiterals.OUTPUT_SCORING: False,
    CommonSettingsLiterals.SAVE_MLFLOW: False,
    DistributedLiterals.DISTRIBUTED: DistributedParameters.DEFAULT_DISTRIBUTED,
    DistributedLiterals.MASTER_ADDR: DistributedParameters.DEFAULT_MASTER_ADDR,
    DistributedLiterals.MASTER_PORT: DistributedParameters.DEFAULT_MASTER_PORT,
    TrainingLiterals.DETAILED_METRICS: True,
    TrainingLiterals.IMBALANCE_RATE_THRESHOLD: 2,
    TrainingLiterals.WEIGHTED_LOSS: 0
}

multiclass_training_settings_defaults = {
    CommonTrainingLiterals.PRIMARY_METRIC: MetricsLiterals.ACCURACY,
    CommonTrainingLiterals.LEARNING_RATE: 0.01,
}

multilabel_training_settings_defaults = {
    CommonTrainingLiterals.PRIMARY_METRIC: MetricsLiterals.IOU,
    CommonTrainingLiterals.LEARNING_RATE: 0.035,
}

vit_model_names = {
    ModelNames.VITS16R224,
    ModelNames.VITB16R224,
    ModelNames.VITL16R224
}

vit_batch_size_defaults = {
    ModelNames.VITS16R224: 128,
    ModelNames.VITB16R224: 48,
    ModelNames.VITL16R224: 10
}

vit_mc_lrs = {
    ModelNames.VITS16R224: 0.0125,
    ModelNames.VITB16R224: 0.0125,
    ModelNames.VITL16R224: 0.001
}

vit_ml_lrs = {
    ModelNames.VITS16R224: 0.025,
    ModelNames.VITB16R224: 0.025,
    ModelNames.VITL16R224: 0.002
}

inference_settings_defaults = {
    CommonScoringLiterals.BATCH_SIZE: 80,
    CommonSettingsLiterals.NUM_WORKERS: 8
}

safe_to_log_vision_classification_settings = {
    TrainingLiterals.DETAILED_METRICS,
    TrainingLiterals.IMBALANCE_RATE_THRESHOLD,
    TrainingLiterals.WEIGHTED_LOSS,
    ModelLiterals.RESIZE_SIZE,
    ModelLiterals.CROP_SIZE,
    ModelLiterals.VALID_RESIZE_SIZE,
    ModelLiterals.VALID_CROP_SIZE,
    ModelLiterals.TRAIN_CROP_SIZE
}

safe_to_log_settings = \
    safe_to_log_automl_settings | \
    safe_to_log_vision_common_settings | \
    safe_to_log_vision_classification_settings

UNSUPPORTED_CLASSIFICATION_METRICS = {
    'weighted_accuracy', 'balanced_accuracy',
    'norm_macro_recall', 'log_loss',
    'matthews_correlation'
}
