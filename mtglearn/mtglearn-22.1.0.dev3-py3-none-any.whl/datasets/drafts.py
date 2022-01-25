from enum import Enum
from datasets import load_dataset


class Expansion(Enum):
    VOW = "VOW"


class Format(Enum):
    PREMIER_DRAFT = "PremierDraft"


def get_draft_data_link(expansion: Expansion, format: Format):
    return f"https://17lands-public.s3.amazonaws.com/analysis_data/draft_data/draft-data.{expansion.value}.{format.value}.tar.gz"
