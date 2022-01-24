# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Constants for classification tasks."""


class DatasetLiterals:
    """Key columns for Dataset"""
    TEXT_COLUMN = 'text'
    DATAPOINT_ID = 'datapoint_id'
    INPUT_IDS = 'input_ids'
    TOKEN_TYPE_IDS = 'token_type_ids'
    ATTENTION_MASK = 'attention_mask'


class MultiLabelParameters:
    """Defining key variables that will be used later on in the training"""
    MAX_LEN = 128
    TRAIN_BATCH_SIZE = 64
    VALID_BATCH_SIZE = 64
    INFERENCE_BATCH_SIZE = 16
    EPOCHS = 3
    LEARNING_RATE = 4e-05
    OUTPUT_EPOCHS_COUNT = 1024
    DROPOUT = 0.3


class MultiClassParameters:
    """Defining key variables that will be used later on in the training"""
    TRAIN_BATCH_SIZE = 32
    VALID_BATCH_SIZE = 32
    EPOCHS = 3
    SAVE_STRATEGY = "no"
    GRADIENT_ACCUMULATION_STEPS = 1
    PAD_TO_MAX_LENGTH = True
    MAX_LEN_PADDING = "max_length"
    MAX_SEQ_LENGTH_128 = 128
    MAX_SEQ_LENGTH_256 = 256
    MAX_SEQ_LENGTH_THRESHOLD = 0.1


class MultiClassInferenceLiterals:
    """Defining names of the artifacts used during multi-class inference"""
    MODEL_FILE_NAME = 'pytorch_model.bin'
    TOKENIZER_FILE_NAME = 'tokenizer_config.json'
    TRAINING_ARGS = 'training_args.bin'
    LABEL_LIST = "label_list.npy"
    MAX_SEQ_LENGTH = "max_seq_length.npy"
