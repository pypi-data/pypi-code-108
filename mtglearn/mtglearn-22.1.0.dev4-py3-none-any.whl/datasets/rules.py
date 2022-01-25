from typing import List
import re
import os

import requests

from ftfy import fix_text
from datasets import Dataset
from datasets.utils.file_utils import cached_path
from attrs import define
import cattrs
from cattrs.gen import make_dict_structure_fn

from ..config import MTGLEARN_CACHE_HOME
from .utils import try_load_dataset, type2features, check_args


RULES_TXT_URL = "https://media.wizards.com/2021/downloads/MagicCompRules%2020211115.txt"
RULES_DATASET_CACHE = os.path.join(MTGLEARN_CACHE_HOME, "rules")

SECTION_RE = re.compile(r"^\d+\.\d*\.?\d*\.?[a-z]? ")
BULLET_RE = re.compile(r"^[a-z] ")


@define
class Rule:
    text: str

    def __str__(self):
        return self.text.strip()


def _process_rule(line: str) -> str:
    line = SECTION_RE.sub("", line)
    line = BULLET_RE.sub("", line)
    line = line.strip()
    return line


def load_rules(
    as_objs=False, as_dataset=False, as_dataframe=False, refresh: bool = False
):

    args = check_args(as_objs=as_objs, as_dataset=as_dataset, as_dataframe=as_dataframe)

    if refresh:
        dataset = None
    else:
        dataset = try_load_dataset(RULES_DATASET_CACHE)

    if dataset is None:

        path = cached_path(RULES_TXT_URL, force_download=refresh)

        with open(path) as f:
            raw_rules = f.read()

        raw_rules = fix_text(raw_rules)
        rules = [_process_rule(line) for line in raw_rules.split("\n")]

        dataset = Dataset.from_dict({"text": rules}, features=type2features(Rule))
        # remove empty lines
        dataset = dataset.filter(lambda x: bool(x["text"]))

        dataset.save_to_disk(RULES_DATASET_CACHE)

    if args.as_dataset:
        return dataset

    if args.as_dataframe:
        return dataset.to_pandas()

    if args.as_objs:
        fromdict = make_dict_structure_fn(Rule, cattrs.Converter())
        return [fromdict(r) for r in dataset]
