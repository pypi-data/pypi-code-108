# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Parameters that apply to model training/scoring"""

from argparse import ArgumentParser
from distutils.util import strtobool
from typing import Any, Dict

from azureml.automl.dnn.vision.common import utils
from azureml.automl.dnn.vision.common.constants import LrSchedulerType, OptimizerType, ScoringLiterals, \
    SettingsLiterals, TrainingLiterals, supported_model_layer_info


def add_task_agnostic_train_parameters(parser: ArgumentParser, default_values: Dict[str, Any]) -> None:
    """Adds to the parser training parameters that are task agnostic.

    :param parser: args parser
    :type parser: ArgumentParser
    :param default_values: default values for the parameters
    :type default_values: dict
    :return: None
    """
    # Model and Device Settings
    utils.add_model_arguments(parser)

    parser.add_argument(utils._make_arg(SettingsLiterals.DEVICE), type=str,
                        help="Device to train on (cpu/cuda:0/cuda:1,...)",
                        default=default_values[SettingsLiterals.DEVICE])

    # Epochs and batch size
    parser.add_argument(utils._make_arg(TrainingLiterals.NUMBER_OF_EPOCHS), type=int,
                        help="Number of training epochs",
                        default=default_values[TrainingLiterals.NUMBER_OF_EPOCHS])

    parser.add_argument(utils._make_arg(TrainingLiterals.TRAINING_BATCH_SIZE), type=int,
                        help="Training batch size",
                        default=default_values[TrainingLiterals.TRAINING_BATCH_SIZE])

    parser.add_argument(utils._make_arg(TrainingLiterals.VALIDATION_BATCH_SIZE), type=int,
                        help="Validation batch size",
                        default=default_values[TrainingLiterals.VALIDATION_BATCH_SIZE])

    parser.add_argument(utils._make_arg(TrainingLiterals.GRAD_ACCUMULATION_STEP), type=int,
                        help="Gradient accumulation means running a configured number of grad_accumulation_step "
                             "without updating the model weights while accumulating the gradients of those steps "
                             "and then using the accumulated gradients to compute the weight updates. ",
                        default=default_values[TrainingLiterals.GRAD_ACCUMULATION_STEP])

    # Early termination
    parser.add_argument(utils._make_arg(TrainingLiterals.EARLY_STOPPING),
                        type=lambda x: bool(strtobool(str(x))),
                        help="Enable early stopping logic during training",
                        default=default_values[TrainingLiterals.EARLY_STOPPING])

    parser.add_argument(utils._make_arg(TrainingLiterals.EARLY_STOPPING_PATIENCE), type=int,
                        help="Minimum number of epochs/validation evaluations "
                             "with no primary metric score improvement before the run is stopped",
                        default=default_values[TrainingLiterals.EARLY_STOPPING_PATIENCE])

    parser.add_argument(utils._make_arg(TrainingLiterals.EARLY_STOPPING_DELAY), type=int,
                        help="Minimum number of epochs/validation evaluations "
                             "to wait before primary metric score improvement is tracked for early stopping",
                        default=default_values[TrainingLiterals.EARLY_STOPPING_DELAY])

    # Learning rate and learning rate scheduler
    parser.add_argument(utils._make_arg(TrainingLiterals.LEARNING_RATE), type=float,
                        help="Initial learning rate",
                        default=default_values[TrainingLiterals.LEARNING_RATE])

    parser.add_argument(utils._make_arg(TrainingLiterals.LR_SCHEDULER), type=str,
                        choices=LrSchedulerType.ALL_TYPES,
                        help="Type of learning rate scheduler in {warmup_cosine, step}",
                        default=default_values[TrainingLiterals.LR_SCHEDULER])

    parser.add_argument(utils._make_arg(TrainingLiterals.STEP_LR_GAMMA), type=float,
                        help="Value of gamma for the learning rate scheduler if it is of type step",
                        default=default_values[TrainingLiterals.STEP_LR_GAMMA])

    parser.add_argument(utils._make_arg(TrainingLiterals.STEP_LR_STEP_SIZE), type=int,
                        help="Value of step_size for the learning rate scheduler if it is of type step",
                        default=default_values[TrainingLiterals.STEP_LR_STEP_SIZE])

    parser.add_argument(utils._make_arg(TrainingLiterals.WARMUP_COSINE_LR_CYCLES), type=float,
                        help="Value of cosine cycle for the learning rate scheduler if it is of type warmup_cosine",
                        default=default_values[TrainingLiterals.WARMUP_COSINE_LR_CYCLES])

    parser.add_argument(utils._make_arg(TrainingLiterals.WARMUP_COSINE_LR_WARMUP_EPOCHS), type=int,
                        help="Value of warmup epochs for the learning rate scheduler if it is of type warmup_cosine",
                        default=default_values[TrainingLiterals.WARMUP_COSINE_LR_WARMUP_EPOCHS])

    # Optimizer
    parser.add_argument(utils._make_arg(TrainingLiterals.OPTIMIZER), type=str,
                        choices=OptimizerType.ALL_TYPES,
                        help="Type of optimizer in {sgd, adam, adamw}",
                        default=default_values[TrainingLiterals.OPTIMIZER])

    parser.add_argument(utils._make_arg(TrainingLiterals.MOMENTUM), type=float,
                        help="Value of momentum for the optimizer if it is of type sgd",
                        default=default_values[TrainingLiterals.MOMENTUM])

    parser.add_argument(utils._make_arg(TrainingLiterals.WEIGHT_DECAY), type=float,
                        help="Value of weight_decay for the optimizer if it is of type sgd or adam or adamw",
                        default=default_values[TrainingLiterals.WEIGHT_DECAY])

    parser.add_argument(utils._make_arg(TrainingLiterals.NESTEROV),
                        type=lambda x: bool(strtobool(str(x))),
                        help="Enable nesterov for the optimizer if it is of type sgd",
                        default=default_values[TrainingLiterals.NESTEROV])

    parser.add_argument(utils._make_arg(TrainingLiterals.BETA1), type=float,
                        help="Value of beta1 for the optimizer if it is of type adam or adamw",
                        default=default_values[TrainingLiterals.BETA1])

    parser.add_argument(utils._make_arg(TrainingLiterals.BETA2), type=float,
                        help="Value of beta2 for the optimizer if it is of type adam or adamw",
                        default=default_values[TrainingLiterals.BETA2])

    parser.add_argument(utils._make_arg(TrainingLiterals.AMSGRAD),
                        type=lambda x: bool(strtobool(str(x))),
                        help="Enable amsgrad for the optimizer if it is of type adam or adamw",
                        default=default_values[TrainingLiterals.AMSGRAD])

    # Evaluation
    parser.add_argument(utils._make_arg(TrainingLiterals.EVALUATION_FREQUENCY), type=int,
                        help="Frequency to evaluate validation dataset to get metric scores",
                        default=default_values[TrainingLiterals.EVALUATION_FREQUENCY])

    parser.add_argument(utils._make_arg(TrainingLiterals.SPLIT_RATIO), type=float,
                        help="Validation split ratio when splitting train data into random train "
                             "and validation subsets if validation data is not defined",
                        default=default_values[TrainingLiterals.SPLIT_RATIO])

    # checkpoint frequency
    parser.add_argument(utils._make_arg(TrainingLiterals.CHECKPOINT_FREQUENCY), type=int,
                        help="Frequency to store model checkpoints. By default, we save checkpoint "
                             "at the epoch which has the best primary metric score on validation")

    # incremental training
    parser.add_argument(utils._make_arg(SettingsLiterals.CHECKPOINT_RUN_ID), type=str,
                        help='The run id of the experiment that has a pretrained checkpoint for incremental training')

    parser.add_argument(utils._make_arg(SettingsLiterals.CHECKPOINT_DATASET_ID), type=str,
                        help="FileDataset id for pretrained checkpoint(s) for incremental training. "
                             "Make sure to pass {} along with {}"
                        .format(SettingsLiterals.CHECKPOINT_FILENAME,
                                SettingsLiterals.CHECKPOINT_DATASET_ID))

    parser.add_argument(utils._make_arg(SettingsLiterals.CHECKPOINT_FILENAME), type=str,
                        help="The pretrained checkpoint filename in FileDataset for incremental training. "
                             "Make sure to pass {} along with {}"
                        .format(SettingsLiterals.CHECKPOINT_DATASET_ID,
                                SettingsLiterals.CHECKPOINT_FILENAME))

    # Layer freezing
    # no default for this argument since this is an model-specific optional argument.
    parser.add_argument(utils._make_arg(TrainingLiterals.LAYERS_TO_FREEZE), type=int,
                        help="How many layers to freeze for your model. Available layers for each model is "
                             "following: {}. For instance, passing 2 as value for seresnext means you want to "
                             "freeze layer0 and layer1. If this is not specified, we default to: "
                             "no frozen layer for resnet18/34/50, mobilenetv2, seresnext and yolov5, "
                             "while the first two layers are frozen in resnet backbone for fasterrcnn, maskrcnn "
                             "and retinanet.".format(supported_model_layer_info))

    # Data path for internal use only. Only labeled datasets is allowed for built-in models
    parser.add_argument(utils._make_arg(SettingsLiterals.DATA_FOLDER),
                        utils._make_arg(SettingsLiterals.DATA_FOLDER.replace("_", "-")), type=str,
                        help="Root of the blob store",
                        default=default_values[SettingsLiterals.DATA_FOLDER])

    parser.add_argument(utils._make_arg(SettingsLiterals.LABELS_FILE_ROOT),
                        utils._make_arg(SettingsLiterals.LABELS_FILE_ROOT.replace("_", "-")), type=str,
                        help="Root relative to which label file paths exist",
                        default=default_values[SettingsLiterals.LABELS_FILE_ROOT])


def add_task_agnostic_scoring_parameters(parser: ArgumentParser, default_values: Dict[str, Any]) -> None:
    """Adds to the parser scoring parameters that are task agnostic.

    :param parser: args parser
    :type parser: ArgumentParser
    :param default_values: default values for the parameters
    :type default_values: dict
    :return: None
    """

    parser.add_argument(utils._make_arg(ScoringLiterals.RUN_ID),
                        help='Experiment run id that generated the model')

    parser.add_argument(utils._make_arg(ScoringLiterals.EXPERIMENT_NAME),
                        help='Experiment that ran the run which generated the model')

    parser.add_argument(utils._make_arg(ScoringLiterals.INPUT_DATASET_ID),
                        help='Input_dataset_id')

    parser.add_argument(utils._make_arg(ScoringLiterals.ROOT_DIR),
                        help='Path to root dir for files listed in image_list_file')

    parser.add_argument(utils._make_arg(ScoringLiterals.IMAGE_LIST_FILE),
                        help='Image files list')

    parser.add_argument(utils._make_arg(ScoringLiterals.OUTPUT_FILE),
                        help='Path to output file')

    parser.add_argument(utils._make_arg(ScoringLiterals.LOG_OUTPUT_FILE_INFO),
                        type=lambda x: bool(strtobool(str(x))),
                        help='Log output file debug info',
                        default=False)

    parser.add_argument(utils._make_arg(ScoringLiterals.BATCH_SIZE), type=int,
                        help='Inference batch_size',
                        default=default_values[ScoringLiterals.BATCH_SIZE])

    parser.add_argument(utils._make_arg(ScoringLiterals.VALIDATE_SCORE),
                        type=lambda x: bool(strtobool(str(x))),
                        help='Validate score if ground truth given in dataset',
                        default=False)
