"""sampling_agent.py
============
The agents for sampling frames
"""

import os
import datetime
import time
from requests.exceptions import ConnectionError
from uuid import uuid4
from io import BytesIO
from google.resumable_media.requests import ResumableUpload
from google.resumable_media.common import InvalidResponse, DataCorruption
from tqdm import tqdm
import sys
from .viridis import viridis_rgb
from .turbo import turbo_rgb
from .issues import IssueManager
import re
from typing import Any, Optional, Union, List, Dict, Tuple
from typing_extensions import TypedDict
import random

from .util import (
    requests_retry,
    assert_valid_name,
    MAX_CHUNK_SIZE,
    raise_resp_exception_error,
    ElementType,
    PrimaryTask,
)
from .dataset import LabeledDataset, LabeledFrame
from .inference import Inferences, InferencesFrame
from abc import ABC, abstractmethod


class SamplingScoreDict(TypedDict, total=False):
    similarity_score: float
    similarity_score_version: str

    # Used for embedding distance sampling v1
    # TODO: Move these over to non-dict protocols so they can
    # be used more flexibly
    sampled_element_id: Optional[str]
    closest_microcluster_idx: Optional[int]
    elt_embedding_vec: Optional[List[float]]
    model_id: Optional[str]


class SamplingAgent(ABC):
    @abstractmethod
    def load_sampling_dataset(
        self,
        element_type: ElementType,
        primary_task: PrimaryTask,
        preprocessed_info: Dict[str, Any],
    ) -> None:
        pass

    @abstractmethod
    def score_frame(self, frame: LabeledFrame) -> SamplingScoreDict:
        pass


class RandomSamplingAgent(SamplingAgent):
    def __init__(self, random_seed: Optional[int] = None) -> None:
        self.random_seed = random_seed

    def load_sampling_dataset(
        self,
        element_type: ElementType,
        primary_task: PrimaryTask,
        preprocessed_info: Dict[str, Any],
    ) -> None:
        # Postprocess here
        return

    def score_frame(self, frame: LabeledFrame) -> SamplingScoreDict:
        random.seed(self.random_seed)
        return {
            "similarity_score": random.random(),  # nosemgrep
            "similarity_score_version": "random_v1",
        }
