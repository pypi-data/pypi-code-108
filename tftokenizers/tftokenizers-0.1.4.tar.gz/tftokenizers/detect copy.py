"""Help identify models, class type, mappings and more"""

import re
from typing import Any, Dict, List, Optional, Tuple, Union

import sentencepiece as spm
import tensorflow as tf
import tensorflow_text as text
from transformers import AutoConfig, AutoTokenizer, PreTrainedTokenizer
from transformers.models.auto.configuration_auto import (
    CONFIG_MAPPING,
    MODEL_NAMES_MAPPING,
    SPECIAL_MODEL_TYPE_TO_MODULE_NAME,
    config_class_to_model_type,
    model_type_to_module_name,
)
from transformers.models.auto.tokenization_auto import (
    CONFIG_TO_TYPE,
    TOKENIZER_MAPPING,
    TOKENIZER_MAPPING_NAMES,
    get_tokenizer_config,
    tokenizer_class_from_name,
)

from tftokenizers.file import get_vocab_from_path, load_json


def get_tokenizer_type(model_name_or_path, path, **kwargs):
    pass


# TODO: could be enum type
def find_tf_base_tokenizer(tokenizer_type, **kwargs):
    pass


def load_tokenizer(tokenizer_tf_base, tokenizer_config_params, **kwargs):
    pass


def detect_and_load_tokenizer(config: PreTrainedTokenizer, path):
    # TODO: Move to detect.py
    """Load the corresponging base tokenizer from Huggingaface and map it to a Tensorflow model."""

    # TODO: map
    # TODO: Find the corresponding base tokenizer and provide all the configs from Huggingface Tokenizer config,
    #   s.a. `max_char_per_token`, `prefix_indicator`

    # TODO: Can be either model (SentencePiece ) or vocab
    vocab_file = config.vocab_files_names["vocab_file"]
    vocab_path = f"{path}/{vocab_file}"

    """
    (vocab_lookup_table: Unknown,
    suffix_indicator: Unknown = "##",
    max_bytes_per_word: Unknown = 100,
    max_chars_per_token: Unknown = None,
    token_out_type: Unknown = dtypes.int64,
    unknown_token: Unknown = "[UNK]",
    split_unknown_characters: Unknown = False,
    lower_case: Unknown = False,
    keep_whitespace: Unknown = False,
    normalization_form: Unknown = None,
    preserve_unused_token: Unknown = False,
    basic_tokenizer_class: Unknown = BasicTokenizer) -> None
    """
    return text.BertTokenizer(
        vocab_path,
        token_out_type=tf.int64,
        lower_case=True,
    )


# def config_class_to_model_type(config):
#     """Converts a config class name to the corresponding model type

#     >>> config = AutoModel.from_pretrained("bert-base-uncased")
#     >>> base_model = config_class_to_model_type(type(config))
#     """
#     for key, cls in CONFIG_MAPPING.items():
#         if cls == config:
#             return key
#     return None


# def model_type_to_module_name(key):
#     """Converts a config key to the corresponding module."""
#     # Special treatment
#     if key in SPECIAL_MODEL_TYPE_TO_MODULE_NAME:
#         return SPECIAL_MODEL_TYPE_TO_MODULE_NAME[key]

#     return key.replace("-", "_")

# NAME_OR_PATH = "bert-base-uncased"
# config = AutoConfig.from_pretrained(NAME_OR_PATH)
# base_name = config_class_to_model_type(type(config).__name__)
# print(base_name)

# model_type = model_type_to_module_name(type(config).__name__)
# print(model_type)


# tokenizer_config = get_tokenizer_config("xlm-roberta-base")
# tokenizer_config = get_tokenizer_config("bert-base-cased")
# print(tokenizer_config)

# # Save a pretrained tokenizer locally and you can reload its config
# tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-base")
# tokenizer.save_pretrained("tokenizer-test")
# tokenizer_config = get_tokenizer_config("tokenizer-test")
# print(tokenizer_config)


"""
In [16]: cb["post_processor"]
Out[16]:
{'type': 'TemplateProcessing',
 'single': [{'SpecialToken': {'id': '[CLS]', 'type_id': 0}},
  {'Sequence': {'id': 'A', 'type_id': 0}},
  {'SpecialToken': {'id': '[SEP]', 'type_id': 0}}],
 'pair': [{'SpecialToken': {'id': '[CLS]', 'type_id': 0}},
  {'Sequence': {'id': 'A', 'type_id': 0}},
  {'SpecialToken': {'id': '[SEP]', 'type_id': 0}},
  {'Sequence': {'id': 'B', 'type_id': 1}},
  {'SpecialToken': {'id': '[SEP]', 'type_id': 1}}],
 'special_tokens': {'[CLS]': {'id': '[CLS]',
   'ids': [101],
   'tokens': ['[CLS]']},
  '[SEP]': {'id': '[SEP]', 'ids': [102], 'tokens': ['[SEP]']}}}
"""
