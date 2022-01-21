import glob

import rich
from tqdm import tqdm
from transformers.models.auto import AutoTokenizer
from transformers.models.auto.configuration_auto import AutoConfig
from transformers.models.auto.tokenization_auto import (
    TOKENIZER_CONFIG_FILE,
    TOKENIZER_MAPPING,
    TOKENIZER_MAPPING_NAMES,
)

from tftokenizers.file import load_json

FIND = "-tokenizer"
REPLACE = ""

ROOT_DIR = "./saved_tokenizers"

print("Changing folder names")
# for old_dir in tqdm(glob.glob(f"{ROOT_DIR}/*")):
#     if FIND in old_dir:
#         new_dir = old_dir.replace(FIND, REPLACE)
#         os.rename(old_dir, new_dir)

# for dir in glob.glob(f"{ROOT_DIR}/*"):
#     for f in glob.glob(f"{dir}/*"):
#         if "special" in f:
#             special_tokens_map = load_json(f)
#         if "tokenizer_config" in f:
#             tokenizer_config = load_json(f)
#     for key in special_tokens_map.keys():
#         if key not in tokenizer_config.keys():
#             print("False", f, dir)

for dir in glob.glob(f"{ROOT_DIR}/*"):
    for f in glob.glob(f"{dir}/*"):
        if ".model" in f:
            print("\nSentencePiece\n:", f, dir)
