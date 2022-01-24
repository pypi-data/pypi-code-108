# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Constants for the package."""

from enum import Enum


class SystemSettings:
    """System settings."""
    NAMESPACE = "azureml.automl.dnn.nlp"
    LABELING_RUNSOURCE = "Labeling"
    LABELING_DATASET_TYPE = "labeling_dataset_type"
    LABELING_DATASET_TYPE_FILEDATSET = "FileDataset"
    LOG_FILENAME = "azureml_automl_nlp.log"
    LOG_FOLDER = "logs"
    # For TrainingArguments to disable hf logging
    LOGGING_STRATEGY = "no"
    REPORT_TO = "none"


class OutputLiterals:
    """Directory and file names for artifacts."""
    NER_MODEL_FILE_NAME = "pytorch_model.bin"
    MODEL_FILE_NAME = "model.pkl"
    VECTORIZER_FILE_NAME = "vectorizer.pkl"
    CHECKPOINT_FILE_NAME = "checkpoint"
    TOKENIZER_FILE_NAME = "tokenizer_config.json"
    CONFIG_FILE_NAME = "config.json"
    CONDA_ENV_NAME = "conda_env.yml"
    OUTPUT_DIR = "./outputs"
    SCORE_SCRIPT = "score_script.py"
    DEPLOY_SCRIPT = "score.py"
    TRAINING_ARGS = "training_args.bin"
    LABELS_FILE = "labels.txt"
    LABEL_LIST_FILE_NAME = "label_list.npy"
    PREDICTIONS_TXT_FILE_NAME = "predictions.txt"
    PREDICTIONS_CSV_FILE_NAME = "predictions.csv"
    ARTIFACT_TYPE_CONFIG = "CONFIG"
    ARTIFACT_TYPE_LABELS = "LABELS"
    ARTIFACT_TYPE_MODEL = "MODEL"
    ARTIFACT_TYPE_TOKENIZER = "TOKENIZER"
    ARTIFACT_TYPE_TRAINING_ARGS = "TRAINING_ARGS"


class DataLiterals:
    """Directory and file names for artifacts."""
    DATASET_ID = "dataset_id"
    VALIDATION_DATASET_ID = "validation_dataset_id"
    DATA_DIR = "data"
    NER_DATA_DIR = "ner_data"
    TRAIN_TEXT_FILENAME = "train.txt"
    VALIDATION_TEXT_FILENAME = "validation.txt"
    TEST_TEXT_FILENAME = "test.txt"
    DATASTORE_PREFIX = "AmlDatastore://"
    NER_IGNORE_TOKENS = ["", " ", "\n"]
    LABEL_COLUMN = "label"
    LABEL_CONFIDENCE = "label_confidence"
    TEXT_COLUMN = "text"
    ENCODING = 'utf-8'
    ERRORS = "replace"


class ScoringLiterals:
    """String names for scoring settings"""
    RUN_ID = "run_id"
    EXPERIMENT_NAME = "experiment_name"
    OUTPUT_FILE = "output_file"
    ROOT_DIR = "root_dir"
    BATCH_SIZE = "batch_size"
    INPUT_DATASET_ID = "input_dataset_id"
    LABEL_COLUMN_NAME = "label_column_name"
    LOG_OUTPUT_FILE_INFO = "log_output_file_info"
    ENABLE_DATAPOINT_ID_OUTPUT = "enable_datapoint_id_output"
    AZUREML_MODEL_DIR_ENV = "AZUREML_MODEL_DIR"


class LoggingLiterals:
    """Literals that help logging and correlating different training runs."""
    PROJECT_ID = "project_id"
    VERSION_NUMBER = "version_number"
    TASK_TYPE = "task_type"


class NERModelParameters:
    """Default model parameters for NER"""
    MAX_SEQ_LENGTH = 128
    NUM_TRAIN_EPOCHS = 3
    OVERWRITE_CACHE = False
    PER_DEVICE_TRAIN_BATCH_SIZE = 32
    TASK_NAME = "ner"
    SAVE_STRATEGY = "no"


class Warnings:
    """Warning strings."""
    CPU_DEVICE_WARNING = "The device being used for training is 'cpu'. Training can be slow and may lead to " \
                         "out of memory errors. Please switch to a compute with gpu devices. " \
                         "If you are already running on a compute with gpu devices, please check to make sure " \
                         "your nvidia drivers are compatible with torch version {}."


class Split(Enum):
    """Split Enum Class."""
    train = "train"
    valid = "valid"
    test = "test"


class TaskNames:
    """Names for NLP DNN tasks"""
    MULTILABEL = "multilabel"
    MULTICLASS = "multiclass"


class ModelNames:
    """Currently supported model names."""
    BERT_BASE_UNCASED = "bert-base-uncased"
    BERT_BASE_CASED = "bert-base-cased"
    BERT_BASE_MULTILINGUAL_CASED = "bert-base-multilingual-cased"
    BERT_BASE_GERMAN_CASED = "bert-base-german-cased"


class DataLabelingLiterals:
    """Constants for Data Labeling specific records"""
    ARGUMENTS = "arguments"
    DATASTORENAME = "datastoreName"
    IMAGE_URL = "image_url"
    RESOURCE_IDENTIFIER = "resource_identifier"
