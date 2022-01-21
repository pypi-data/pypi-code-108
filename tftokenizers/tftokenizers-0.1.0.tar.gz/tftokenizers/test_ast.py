from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import numpy as np
import tensorflow as tf
from pydantic import BaseModel
from transformers.models.auto import AutoTokenizer
from transformers.models.auto.configuration_auto import AutoConfig
from transformers.models.auto.tokenization_auto import (
    TOKENIZER_CONFIG_FILE,
    TOKENIZER_MAPPING,
    TOKENIZER_MAPPING_NAMES,
)

# from tf_transformers.convert import get_special_tokens_value, map_special_tokens_to_ids
from tf_transformers.file import get_vocab_from_path, load_json
from tf_transformers.types import PROCESSING_STEP
from tf_transformers.utils import map_special_tokens_to_ids

# MODEL_NAME = "bert-base-uncased"
# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
# config = AutoConfig.from_pretrained(MODEL_NAME)
# special_tokens_map: Dict[str, str] = tokenizer.special_tokens_map
# special_tokens = SpecialTokens(**special_tokens_map)

# vocab_file, tokenizer_file = tokenizer.vocab_files_names.values()
# tokenizer.save_pretrained(f"save_pretrained/{MODEL_NAME}")
# tokenizer_config = parse_config(tokenizer_file)

# # Next, map the tokenizer to the base tokenizer config (BertTokenizer, RobertaTokenizer)
# # Can map  "post_processor": `TemplateProcessing`: "single" special characters to
# #   find token in special_tokens_map. Return it and the value


# # Load configs and special tokens
# tokenizer_class_py, tokenizer_class_fast = TOKENIZER_MAPPING[type(config)]
# print(tokenizer_class_py)


# print()
# print(tokenizer_class_fast)
# # BertForMaskedLM = config.architecture[0]
# # bert = config.model_type


vocab_path = "saved_tokenizers/bert-base-uncased/vocab.txt"  # TODO:
vocab = get_vocab_from_path("./saved_tokenizers/bert-base-uncased/vocab.txt")
config_huggingface = load_json("saved_tokenizers/bert-base-uncased/tokenizer.json")
special_tokens = load_json("saved_tokenizers/bert-base-uncased/special_tokens_map.json")

# Tokenizer config
config_huggingface["model"].pop(
    "vocab"
)  # TODO: Also remove `precompiled/ pre_compiled`
tokenizer_truncate = config_huggingface["truncation"]
tokenizer_padding = config_huggingface["padding"]

# Tokenizer pipeline steps
tokenizer_normalizer = config_huggingface["normalizer"]
tokenizer_pre_tokenizer = config_huggingface["pre_tokenizer"]
tokenizer_post_processor = config_huggingface["post_processor"]

# Tokenizer base model
tokenizer_base_model = config_huggingface["model"]["type"]
tokenizer_unk_token = config_huggingface["model"]["unk_token"]

# TODO should not be needed when updating
special_tokens_by_name, special_tokens_map = map_special_tokens_to_ids(
    vocab, special_tokens
)


def post_process(bs):
    """
    #TODO
    """
    processing_template = config_huggingface["post_processor"]["single"]
    processing_template = processing_template[1]
    num_sentences = bs.shape[0]

    def parse_template_step_to_token_id(
        instruction_step: PROCESSING_STEP,
    ):
        token_symbol = list(instruction_step.values())[0]["id"]
        token_id = special_tokens_map.get(token_symbol)
        return token_id

    def np_fill(num_sentences, value):
        return np.array([[value] for _ in range(num_sentences)])

    # Build AST from instructions
    num_steps = len(processing_template)
    # if num_steps == 1:
    #     print("asdasd")
    #     return bs

    for step in range(num_steps - 1):
        left: PROCESSING_STEP = processing_template[step]
        right: PROCESSING_STEP = processing_template[(step + 1) - num_steps]
        left_token = parse_template_step_to_token_id(left)
        right_token = parse_template_step_to_token_id(right)

        if left != right:
            left_sentence = bs
            right_sentence = bs

            if "SpecialToken" in left:
                left_sentence = np_fill(num_sentences, left_token)
            elif "SpecialToken" in right:
                right_sentence = np_fill(num_sentences, right_token)
            bs = np.concatenate((left_sentence, right_sentence), axis=1)
            print("\n\nStep:", step)
            print("left:", left, left_sentence)
            print("right:", right, right_sentence)
            print(bs)
    return bs


input_data = (
    tf.ragged.constant(
        [
            # [101, 1, 2, 102, 10, 20, 102],
            # [101, 3, 4, 102, 30, 40, 50, 60, 70, 80],
            # [101, 5, 6, 7, 8, 9, 102, 70],
            [1, 2, 102, 10, 20],
            [3, 4, 102, 30, 40, 50, 60, 70, 80],
            [5, 6, 7, 8, 9, 102, 70],
        ],
        tf.int32,
    )
    .to_tensor()
    .numpy()
)

v = post_process(input_data)
print(v)
