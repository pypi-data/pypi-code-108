# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Constants for the package."""

from typing import Dict, Any
import os
import torch


class ArtifactLiterals:
    """Filenames for artifacts."""
    FEATURIZE_SCRIPT = 'featurize_script.py'
    LABEL_FILE_NAME = 'labels.json'
    PER_LABEL_METRICS_FILE_NAME = "per_label_metrics.json"
    ONNX_MODEL_FILE_NAME = 'model.onnx'
    OUTPUT_DIR = 'train_artifacts'
    SCORE_SCRIPT = 'score_script.py'
    TRAIN_SUB_FILE_NAME = "train_sub.json"
    VAL_SUB_FILE_NAME = "val_sub.json"


class SystemMetricsLiterals:
    """String key names for system metrics."""
    SCRIPT_DURATION_SECONDS = "script_duration_seconds"

    TRAIN_DURATION_SECONDS = "train_duration_seconds"
    TRAIN_EPOCH_COUNT = "train_epoch_count"

    TRAIN_EPOCH_DURATION_SECONDS_AVG = "train_epoch_duration_seconds_avg"
    TRAIN_EPOCH_DURATION_SECONDS_MAX = "train_epoch_duration_seconds_max"

    TRAIN_GPU_MEM_USED_MB_AVG = "train_gpu_mem_used_mb_avg"
    TRAIN_GPU_MEM_USED_MB_MAX = "train_gpu_mem_used_mb_max"

    TRAIN_GPU_USED_PCT_AVG = "train_gpu_used_pct_avg"
    TRAIN_GPU_USED_PCT_MAX = "train_gpu_used_pct_max"

    TRAIN_SYS_MEM_PCT_AVG = "train_sys_mem_pct_avg"
    TRAIN_SYS_MEM_PCT_MAX = "train_sys_mem_pct_max"

    TRAIN_SYS_MEM_SHARED_MB_AVG = "train_sys_mem_shared_mb_avg"
    TRAIN_SYS_MEM_SHARED_MB_MAX = "train_sys_mem_shared_mb_max"

    TRAIN_SYS_MEM_USED_MB_AVG = "train_sys_mem_used_mb_avg"
    TRAIN_SYS_MEM_USED_MB_MAX = "train_sys_mem_used_mb_max"

    VALID_GPU_MEM_USED_MB_AVG = "valid_gpu_mem_used_mb_avg"
    VALID_GPU_MEM_USED_MB_MAX = "valid_gpu_mem_used_mb_max"

    VALID_GPU_USED_PCT_AVG = "valid_gpu_used_pct_avg"
    VALID_GPU_USED_PCT_MAX = "valid_gpu_used_pct_max"

    VALID_SYS_MEM_PCT_AVG = "valid_sys_mem_pct_avg"
    VALID_SYS_MEM_PCT_MAX = "valid_sys_mem_pct_max"

    VALID_SYS_MEM_SHARED_MB_AVG = "valid_sys_mem_shared_mb_avg"
    VALID_SYS_MEM_SHARED_MB_MAX = "valid_sys_mem_shared_mb_max"

    VALID_SYS_MEM_USED_MB_AVG = "valid_sys_mem_used_mb_avg"
    VALID_SYS_MEM_USED_MB_MAX = "valid_sys_mem_used_mb_max"


class MetricsLiterals:
    """String key names for evaluation metrics."""
    ACCURACY = 'accuracy'
    PRECISION = 'precision'
    RECALL = 'recall'
    SUPPORT = 'support'
    F1_SCORE = 'f1-score'
    AVERAGE_PRECISION = 'average_precision'
    AUC = 'auc'
    ACCURACY_TOP5 = 'accuracy_top5'
    IOU = 'iou'
    MACRO = 'macro'
    MICRO = 'micro'
    WEIGHTED = 'weighted'
    MEAN_AVERAGE_PRECISION = 'mean_average_precision'
    CONFUSION_MATRIX = 'confusion_matrix'
    AUTOML_CLASSIFICATION_EVAL_METRICS = 'automl_classification_eval_metrics'
    AUTOML_CLASSIFICATION_TRAIN_METRICS = 'automl_classification_train_metrics'
    COCO_METRICS = 'coco_metrics'
    PER_LABEL_METRICS = 'per_label_metrics'
    CLASS_NAME = 'class_name'
    CLASS_LABELS = 'class_labels'
    MATRIX = 'matrix'
    DATA = 'data'
    AVERAGE = 'average'
    TOTAL_SCORE_TIME_SEC = 'total_score_time_sec'
    PER_IMAGE_AVG_SCORE_TIME_SEC = 'per_image_avg_score_time_sec'


class SystemSettings:
    """System settings."""
    NAMESPACE = 'azureml.automl.dnn.vision'
    LOG_FILENAME = 'azureml_automl_vision.log'
    LOG_FOLDER = 'logs'


class PretrainedModelNames:
    """Pre trained model names."""
    RESNET18 = 'resnet18'
    RESNET34 = 'resnet34'
    RESNET50 = 'resnet50'
    RESNET101 = 'resnet101'
    RESNET152 = 'resnet152'
    RESNEST50 = 'resnest50'
    RESNEST101 = 'resnest101'
    MOBILENET_V2 = 'mobilenet_v2'
    SE_RESNEXT50_32X4D = 'se_resnext50_32x4d'
    VITB16R224 = 'vitb16r224'
    VITS16R224 = 'vits16r224'
    VITL16R224 = 'vitl16r224'
    FASTERRCNN_RESNET18_FPN_COCO = 'fasterrcnn_resnet18_fpn_coco'
    FASTERRCNN_RESNET34_FPN_COCO = 'fasterrcnn_resnet34_fpn_coco'
    FASTERRCNN_RESNET50_FPN_COCO = 'fasterrcnn_resnet50_fpn_coco'
    FASTERRCNN_RESNET101_FPN_COCO = 'fasterrcnn_resnet101_fpn_coco'
    FASTERRCNN_RESNET152_FPN_COCO = 'fasterrcnn_resnet152_fpn_coco'
    MASKRCNN_RESNET18_FPN_COCO = 'maskrcnn_resnet18_fpn_coco'
    MASKRCNN_RESNET34_FPN_COCO = 'maskrcnn_resnet34_fpn_coco'
    MASKRCNN_RESNET50_FPN_COCO = 'maskrcnn_resnet50_fpn_coco'
    MASKRCNN_RESNET101_FPN_COCO = 'maskrcnn_resnet101_fpn_coco'
    MASKRCNN_RESNET152_FPN_COCO = 'maskrcnn_resnet152_fpn_coco'
    YOLOV5_SMALL = 'yolov5.3.0s'
    YOLOV5_MEDIUM = 'yolov5.3.0m'
    YOLOV5_LARGE = 'yolov5.3.0l'
    YOLOV5_XLARGE = 'yolov5.3.0x'
    RETINANET_RESNET50_FPN_COCO = 'retinanet_resnet50_fpn_coco'


class RunPropertyLiterals:
    """String keys important for finding the best run."""
    PIPELINE_SCORE = 'score'


class ScoringLiterals:
    """String names for scoring settings"""
    BATCH_SIZE = 'batch_size'
    DEFAULT_OUTPUT_DIR = 'outputs'
    EXPERIMENT_NAME = 'experiment_name'
    FEATURE_FILE_NAME = 'features.txt'
    FEATURIZATION_OUTPUT_FILE = 'featurization_output_file'
    IMAGE_LIST_FILE = 'image_list_file'
    INPUT_DATASET_ID = 'input_dataset_id'
    LABELED_DATASET_FILE_NAME = 'labeled_dataset.json'
    OUTPUT_FILE = 'output_file'
    OUTPUT_FEATURIZATION = 'output_featurization'
    PREDICTION_FILE_NAME = 'predictions.txt'
    ROOT_DIR = 'root_dir'
    RUN_ID = 'run_id'
    VALIDATE_SCORE = 'validate_score'
    LOG_OUTPUT_FILE_INFO = 'log_output_file_info'


class TrainingLiterals:
    """String keys for training parameters."""
    PRIMARY_METRIC = "primary_metric"
    LEARNING_RATE = "learning_rate"
    NUMBER_OF_EPOCHS = "number_of_epochs"
    TRAINING_BATCH_SIZE = "training_batch_size"
    VALIDATION_BATCH_SIZE = "validation_batch_size"
    GRAD_ACCUMULATION_STEP = 'grad_accumulation_step'
    EARLY_STOPPING = "early_stopping"
    EARLY_STOPPING_PATIENCE = "early_stopping_patience"
    EARLY_STOPPING_DELAY = "early_stopping_delay"
    OPTIMIZER = 'optimizer'
    MOMENTUM = 'momentum'
    WEIGHT_DECAY = 'weight_decay'
    NESTEROV = 'nesterov'
    BETA1 = 'beta1'
    BETA2 = 'beta2'
    AMSGRAD = 'amsgrad'
    LR_SCHEDULER = 'lr_scheduler'
    STEP_LR_GAMMA = 'step_lr_gamma'
    STEP_LR_STEP_SIZE = 'step_lr_step_size'
    WARMUP_COSINE_LR_CYCLES = "warmup_cosine_lr_cycles"
    WARMUP_COSINE_LR_WARMUP_EPOCHS = 'warmup_cosine_lr_warmup_epochs'
    GRAD_CLIP_TYPE = "grad_clip_type"
    EVALUATION_FREQUENCY = "evaluation_frequency"
    SPLIT_RATIO = 'split_ratio'
    LAYERS_TO_FREEZE = 'layers_to_freeze'
    CHECKPOINT_FREQUENCY = 'checkpoint_frequency'


class SettingsLiterals:
    """String names for automl settings"""
    CHECKPOINT_FILENAME = 'checkpoint_filename'
    CHECKPOINT_DATASET_ID = 'checkpoint_dataset_id'
    CHECKPOINT_RUN_ID = 'checkpoint_run_id'
    DATA_FOLDER = 'data_folder'
    DATASET_ID = 'dataset_id'
    DEVICE = 'device'
    DETERMINISTIC = 'deterministic'
    ENABLE_ONNX_NORMALIZATION = 'enable_onnx_normalization'
    IGNORE_DATA_ERRORS = 'ignore_data_errors'
    IMAGE_FOLDER = 'images_folder'
    LABELS_FILE = 'labels_file'
    LABELS_FILE_ROOT = 'labels_file_root'
    LOG_SCORING_FILE_INFO = 'log_scoring_file_info'
    LOG_VERBOSE_METRICS = 'log_verbose_metrics'
    MODEL = 'model'
    MODEL_NAME = 'model_name'
    MULTILABEL = 'multilabel'
    NUM_WORKERS = 'num_workers'
    OUTPUT_DIR = 'output_dir'
    OUTPUT_DATASET_TARGET_PATH = 'output_dataset_target_path'
    OUTPUT_SCORING = 'output_scoring'
    PRINT_LOCAL_PACKAGE_VERSIONS = 'print_local_package_versions'
    RANDOM_SEED = 'seed'
    SAVE_MLFLOW = 'save_mlflow'
    TASK_TYPE = 'task_type'
    VALIDATION_DATASET_ID = 'validation_dataset_id'
    VALIDATION_LABELS_FILE = 'validation_labels_file'
    VALIDATION_OUTPUT_FILE = 'validation_output_file'
    VALIDATE_SCORING = 'validate_scoring'


class PretrainedModelUrls:
    """The urls of the pretrained models which are stored in the CDN."""

    MODEL_FOLDER_URL = 'https://aka.ms/automl-resources/data/models-vision-pretrained'
    PREVIEW_WEIGHTS_URL = 'https://aka.ms/automl-research-resources/data/models-vision-pretrained'

    MODEL_URLS = {
        PretrainedModelNames.RESNET18:
            '{}/{}'.format(MODEL_FOLDER_URL, 'resnet18-5c106cde.pth'),
        PretrainedModelNames.RESNET34:
            '{}/{}'.format(PREVIEW_WEIGHTS_URL, 'resnet34-333f7ec4.pth'),
        PretrainedModelNames.RESNET50:
            '{}/{}'.format(MODEL_FOLDER_URL, 'resnet50-19c8e357.pth'),
        PretrainedModelNames.RESNET101:
            '{}/{}'.format(PREVIEW_WEIGHTS_URL, 'resnet101-5d3b4d8f.pth'),
        PretrainedModelNames.RESNET152:
            '{}/{}'.format(PREVIEW_WEIGHTS_URL, 'resnet152-b121ed2d.pth'),
        PretrainedModelNames.RESNEST50:
            '{}/{}'.format(MODEL_FOLDER_URL, 'resnest50-528c19ca.pth'),
        PretrainedModelNames.RESNEST101:
            '{}/{}'.format(MODEL_FOLDER_URL, 'resnest101-22405ba7.pth'),
        PretrainedModelNames.MOBILENET_V2:
            '{}/{}'.format(MODEL_FOLDER_URL, 'mobilenet_v2-b0353104.pth'),
        PretrainedModelNames.SE_RESNEXT50_32X4D:
            '{}/{}'.format(MODEL_FOLDER_URL, 'se_resnext50_32x4d-a260b3a4.pth'),
        PretrainedModelNames.VITB16R224:
            '{}/{}'.format(MODEL_FOLDER_URL, 'vitb16r224-3c68ea1f.pth'),
        PretrainedModelNames.VITS16R224:
            '{}/{}'.format(MODEL_FOLDER_URL, 'vits16r224-ea175c03.pth'),
        PretrainedModelNames.VITL16R224:
            '{}/{}'.format(MODEL_FOLDER_URL, 'vitl16r224-714c5d75.pth'),
        PretrainedModelNames.FASTERRCNN_RESNET50_FPN_COCO:
            '{}/{}'.format(MODEL_FOLDER_URL, 'fasterrcnn_resnet50_fpn_coco-258fb6c6.pth'),
        PretrainedModelNames.MASKRCNN_RESNET50_FPN_COCO:
            '{}/{}'.format(MODEL_FOLDER_URL, 'maskrcnn_resnet50_fpn_coco-bf2d0c1e.pth'),
        PretrainedModelNames.RETINANET_RESNET50_FPN_COCO:
            '{}/{}'.format(MODEL_FOLDER_URL, 'retinanet_resnet50_fpn_coco-eeacb38b.pth'),
        PretrainedModelNames.YOLOV5_SMALL:
            '{}/{}'.format(MODEL_FOLDER_URL, 'yolov5.3.0s-3058c1cb.pth'),
        PretrainedModelNames.YOLOV5_MEDIUM:
            '{}/{}'.format(MODEL_FOLDER_URL, 'yolov5.3.0m-a04eea56.pth'),
        PretrainedModelNames.YOLOV5_LARGE:
            '{}/{}'.format(MODEL_FOLDER_URL, 'yolov5.3.0l-84ff5751.pth'),
        PretrainedModelNames.YOLOV5_XLARGE:
            '{}/{}'.format(MODEL_FOLDER_URL, 'yolov5.3.0x-be3180f8.pth'),
        PretrainedModelNames.FASTERRCNN_RESNET18_FPN_COCO:
            '{}/{}'.format(PREVIEW_WEIGHTS_URL, 'fasterrcnn-resnet18-fpn-coco-ca1522e9.pth'),
        PretrainedModelNames.FASTERRCNN_RESNET34_FPN_COCO:
            '{}/{}'.format(PREVIEW_WEIGHTS_URL, 'fasterrcnn-resnet34-fpn-coco-815d0bf4.pth'),
        PretrainedModelNames.FASTERRCNN_RESNET101_FPN_COCO:
            '{}/{}'.format(PREVIEW_WEIGHTS_URL, 'fasterrcnn-resnet101-fpn-coco-717a8ffd.pth'),
        PretrainedModelNames.FASTERRCNN_RESNET152_FPN_COCO:
            '{}/{}'.format(PREVIEW_WEIGHTS_URL, 'fasterrcnn-resnet152-fpn-coco-45ef5715.pth'),
        PretrainedModelNames.MASKRCNN_RESNET18_FPN_COCO:
            '{}/{}'.format(PREVIEW_WEIGHTS_URL, 'maskrcnn-resnet18-fpn-coco-490ad435.pth'),
        PretrainedModelNames.MASKRCNN_RESNET34_FPN_COCO:
            '{}/{}'.format(PREVIEW_WEIGHTS_URL, 'maskrcnn-resnet34-fpn-coco-2d232103.pth'),
        PretrainedModelNames.MASKRCNN_RESNET101_FPN_COCO:
            '{}/{}'.format(PREVIEW_WEIGHTS_URL, 'maskrcnn-resnet101-fpn-coco-57b6565d.pth'),
        PretrainedModelNames.MASKRCNN_RESNET152_FPN_COCO:
            '{}/{}'.format(PREVIEW_WEIGHTS_URL, 'maskrcnn-resnet152-fpn-coco-777a4e4d.pth')
    }


class PretrainedSettings:
    """Settings related to fetching pretrained models."""
    DOWNLOAD_RETRY_COUNT = 3


class OptimizerType:
    """String names for optimizer type"""
    SGD = 'sgd'
    ADAM = 'adam'
    ADAMW = 'adamw'
    ALL_TYPES = [SGD, ADAM, ADAMW]


class LrSchedulerType:
    """String names for lr scheduler type"""
    WARMUP_COSINE = 'warmup_cosine'
    STEP = 'step'
    ALL_TYPES = [WARMUP_COSINE, STEP]


class GradClipType:
    """String names for gradient clipping type"""
    VALUE = 'value'
    NORM = 'norm'


class TrainingCommonSettings:
    """Model-agnostic settings for training."""
    GRADIENT_CLIP_VALUE = 5.0
    GRADIENT_CLIP_NORM = 1.0
    MAX_LOSS_VALUE = 100
    DEFAULT_GRAD_CLIP_TYPE = GradClipType.VALUE
    DEFAULT_VIT_GRAD_CLIP_TYPE = GradClipType.NORM
    DEFAULT_EARLY_STOPPING = True
    DEFAULT_EARLY_STOPPING_PATIENCE = 5
    DEFAULT_EARLY_STOPPING_DELAY = 5
    DEFAULT_GRAD_ACCUMULATION_STEP = 1
    DEFAULT_OPTIMIZER = OptimizerType.SGD
    DEFAULT_MOMENTUM = 0.9
    DEFAULT_WEIGHT_DECAY = 1e-4
    DEFAULT_NESTEROV = True
    DEFAULT_BETA1 = 0.9
    DEFAULT_BETA2 = 0.999
    DEFAULT_AMSGRAD = False
    DEFAULT_LR_SCHEDULER = LrSchedulerType.WARMUP_COSINE
    DEFAULT_STEP_LR_GAMMA = 0.5
    DEFAULT_STEP_LR_STEP_SIZE = 5
    DEFAULT_WARMUP_COSINE_LR_CYCLES = 0.45
    DEFAULT_WARMUP_COSINE_LR_WARMUP_EPOCHS = 2
    DEFAULT_EVALUATION_FREQUENCY = 1
    DEFAULT_SPLIT_RATIO = 0.2


class CommonSettings:
    """Model-agnostic general settings."""
    DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    DATA_FOLDER = ''
    LABELS_FILE_ROOT = ''
    TORCH_HUB_CHECKPOINT_DIR = os.path.join(torch.hub.get_dir(), 'checkpoints')


class DistributedLiterals:
    """String keys for distributed parameters."""
    DISTRIBUTED = "distributed"
    MASTER_ADDR = "MASTER_ADDR"
    MASTER_PORT = "MASTER_PORT"
    WORLD_SIZE = "world_size"


class DistributedParameters:
    """Default distributed parameters."""
    DEFAULT_DISTRIBUTED = True
    DEFAULT_BACKEND = "nccl"
    DEFAULT_MASTER_ADDR = "127.0.0.1"
    DEFAULT_MASTER_PORT = "29500"  # TODO: What if this port is not available.
    DEFAULT_RANDOM_SEED = 47


class Warnings:
    """Warning strings."""
    CPU_DEVICE_WARNING = "The device being used for training is 'cpu'. Training can be slow and may lead to " \
                         "out of memory errors. Please switch to a compute with gpu devices. " \
                         "If you are already running on a compute with gpu devices, please check to make sure " \
                         "your nvidia drivers are compatible with torch version {}."


supported_model_layer_info: Dict[str, Any] = {
    'resnet': [('conv1.', 'bn1.'), 'layer1.', 'layer2.', 'layer3.', 'layer4.'],
    'mobilenetv2': ['features.0.', 'features.1.', 'features.2.', 'features.3.', 'features.4.', 'features.5.',
                    'features.6.', 'features.7.', 'features.8.', 'features.9.', 'features.10.', 'features.11.',
                    'features.12.', 'features.13.', 'features.14.', 'features.15.', 'features.16.', 'features.17.',
                    'features.18.'],
    'seresnext': ['layer0.', 'layer1.', 'layer2.', 'layer3.', 'layer4.'],
    'vit': ['patch_embed', 'blocks.0.', 'blocks.1.', 'blocks.2.', 'blocks.3.', 'blocks.4.', 'blocks.5.', 'blocks.6.',
            'blocks.7.', 'blocks.8.', 'blocks.9.', 'blocks.10.', 'blocks.11.'],
    'yolov5_backbone': ['model.0.', 'model.1.', 'model.2.', 'model.3.', 'model.4.',
                        'model.5.', 'model.6.', 'model.7.', 'model.8.', 'model.9.'],
    # By default, conv1 and layer1 are frozen in resnet backbone for fasterrcnn, maskrcnn and retinanet
    # resnet_fpn_backbone() in automl.dnn.vision.common.pretrained_model_utilities
    'resnet_backbone': ['backbone.body.conv1.', 'backbone.body.layer1.', 'backbone.body.layer2.',
                        'backbone.body.layer3.', 'backbone.body.layer4.']
}

safe_to_log_vision_common_settings = {
    TrainingLiterals.PRIMARY_METRIC,
    TrainingLiterals.LEARNING_RATE,
    TrainingLiterals.EARLY_STOPPING,
    TrainingLiterals.EARLY_STOPPING_DELAY,
    TrainingLiterals.EARLY_STOPPING_PATIENCE,
    TrainingLiterals.NUMBER_OF_EPOCHS,
    TrainingLiterals.TRAINING_BATCH_SIZE,
    TrainingLiterals.VALIDATION_BATCH_SIZE,
    TrainingLiterals.GRAD_ACCUMULATION_STEP,
    TrainingLiterals.OPTIMIZER,
    TrainingLiterals.MOMENTUM,
    TrainingLiterals.WEIGHT_DECAY,
    TrainingLiterals.NESTEROV,
    TrainingLiterals.BETA1,
    TrainingLiterals.BETA2,
    TrainingLiterals.AMSGRAD,
    TrainingLiterals.LR_SCHEDULER,
    TrainingLiterals.STEP_LR_GAMMA,
    TrainingLiterals.STEP_LR_STEP_SIZE,
    TrainingLiterals.WARMUP_COSINE_LR_CYCLES,
    TrainingLiterals.WARMUP_COSINE_LR_WARMUP_EPOCHS,
    TrainingLiterals.GRAD_CLIP_TYPE,
    TrainingLiterals.EVALUATION_FREQUENCY,
    TrainingLiterals.CHECKPOINT_FREQUENCY,
    TrainingLiterals.SPLIT_RATIO,
    TrainingLiterals.LAYERS_TO_FREEZE,
    # SettingsLiterals.DATA_FOLDER # not safe
    SettingsLiterals.DATASET_ID,
    SettingsLiterals.DEVICE,
    SettingsLiterals.DETERMINISTIC,
    SettingsLiterals.ENABLE_ONNX_NORMALIZATION,
    SettingsLiterals.IGNORE_DATA_ERRORS,
    # SettingsLiterals.IMAGE_FOLDER # not safe
    SettingsLiterals.CHECKPOINT_FILENAME,
    SettingsLiterals.CHECKPOINT_DATASET_ID,
    SettingsLiterals.CHECKPOINT_RUN_ID,
    # SettingsLiterals.LABELS_FILE # not safe
    # SettingsLiterals.LABELS_FILE_ROOT # not safe
    SettingsLiterals.LOG_SCORING_FILE_INFO,
    SettingsLiterals.LOG_VERBOSE_METRICS,
    SettingsLiterals.MODEL_NAME,
    SettingsLiterals.MULTILABEL,
    SettingsLiterals.NUM_WORKERS,
    SettingsLiterals.OUTPUT_DIR,
    # SettingsLiterals.OUTPUT_DATASET_TARGET_PATH, # not safe
    SettingsLiterals.OUTPUT_SCORING,
    SettingsLiterals.PRINT_LOCAL_PACKAGE_VERSIONS,
    SettingsLiterals.RANDOM_SEED,
    SettingsLiterals.SAVE_MLFLOW,
    SettingsLiterals.TASK_TYPE,
    SettingsLiterals.VALIDATION_DATASET_ID,
    # SettingsLiterals.VALIDATION_LABELS_FILE # not safe
    # SettingsLiterals.VALIDATION_OUTPUT_FILE, # not safe
    SettingsLiterals.VALIDATE_SCORING,

    ScoringLiterals.BATCH_SIZE,
    ScoringLiterals.DEFAULT_OUTPUT_DIR,
    # ScoringLiterals.EXPERIMENT_NAME, # not safe
    # This can stay as it is not exposed
    ScoringLiterals.FEATURE_FILE_NAME,
    # This can stay as it is not exposed
    ScoringLiterals.FEATURIZATION_OUTPUT_FILE,
    # ScoringLiterals.IMAGE_LIST_FILE,  # not safe
    ScoringLiterals.INPUT_DATASET_ID,
    # ScoringLiterals.OUTPUT_FILE,  # not safe
    ScoringLiterals.OUTPUT_FEATURIZATION,
    # ScoringLiterals.PREDICTION_FILE_NAME,  # not safe
    # ScoringLiterals.ROOT_DIR,  # not safe
    ScoringLiterals.RUN_ID,
    ScoringLiterals.VALIDATE_SCORE
}

# most of these settings do not have any effect on vision workflow
# but we'll log them in case we need to analyse a side effect that they might create
safe_to_log_automl_settings = {
    '_debug_log',
    '_ignore_package_version_incompatibilities',
    '_local_managed_run_id',
    'allowed_private_models',
    'auto_blacklist',
    'azure_service',
    'blacklist_algos',
    'blacklist_samples_reached',
    'compute_target',
    'cost_mode',
    'cv_split_column_names',
    'data_script',
    'early_stopping_n_iters',
    'enable_dnn',
    'enable_early_stopping',
    'enable_ensembling',
    'enable_feature_sweeping',
    'enable_local_managed',
    'enable_nimbusml',
    'enable_onnx_compatible_models',
    'enable_split_onnx_featurizer_estimator_models',
    'enable_stack_ensembling',
    'enable_streaming',
    'enable_subsampling',
    'enable_tf',
    'enforce_time_on_windows',
    'ensemble_iterations',
    'environment_label',
    'exclude_nan_labels',
    'experiment_exit_score',
    'experiment_timeout_minutes',
    'featurization',
    'force_streaming',
    'force_text_dnn',
    'is_gpu'
    'is_timeseries',
    'iteration_timeout_minutes',
    'iterations',
    'lag_length',
    'many_models',
    'max_concurrent_iterations',
    'max_cores_per_iteration',
    'mem_in_mb',
    'metric_operation',
    'metrics',
    'model_explainability',
    'n_cross_validations',
    'num_classes',
    'pipeline_fetch_max_batch_size',
    'preprocess',
    'region',
    'resource_group',
    'save_mlflow',
    'scenario',
    'sdk_packages',
    'sdk_url',
    'send_telemetry',
    'service_url',
    'show_warnings',
    'spark_service',
    'subsample_seed',
    'subscription_id',
    'supported_models',
    'task_type',
    'telemetry_verbosity',
    'track_child_runs',
    'validation_size',
    'verbosity',
    'vm_type',
    'weight_column_name',
    'whitelist_models',
    'workspace_name',
    'y_max',
    'y_min',
}
