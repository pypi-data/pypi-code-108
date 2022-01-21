from typing import Any, Optional, Union, List, Dict, Tuple, cast
from typing_extensions import TypedDict
from .sampling_agent import SamplingAgent, SamplingScoreDict
from .dataset import LabeledDataset, LabeledFrame, GTFrameWithEmbeddings
from .util import ElementType, EmbeddingVec, PrimaryTask

import joblib  # type: ignore
import json
import pandas as pd
import pyarrow as pa
import numpy as np
from sklearn.preprocessing import normalize  # type: ignore


class FilteredEmbeddingShapeDict(TypedDict):
    uuid: str
    embedding: EmbeddingVec


class EmbeddingDistanceSamplingAgent(SamplingAgent):

    element_type: Optional[ElementType]
    pca: Optional[Any]
    microclusters: Optional[Any]
    microcluster_centroids: Optional[Any]
    microcluster_radii: Optional[Any]

    def __init__(self, random_seed: Optional[int] = None) -> None:
        self.random_seed = random_seed
        self.element_type = None

        self.pca = None
        self.microclusters = None
        self.microcluster_centroids = None
        self.microcluster_radii = None

    def load_sampling_dataset(
        self,
        element_type: ElementType,
        primary_task: PrimaryTask,
        preprocessed_info: Dict[str, Any],
    ) -> None:
        self.element_type = element_type  # "crop" or "frame"
        self.primary_task = primary_task
        self.pca = joblib.load(preprocessed_info["pca_path"])

        df = pa.ipc.open_file(preprocessed_info["microcluster_info_path"]).read_pandas()
        self.microclusters = df["microclusters"].to_numpy().tolist()
        self.microcluster_centroids = df["microcluster_centroids"].to_numpy().tolist()
        self.microcluster_radii = df["microcluster_radii"].to_numpy().tolist()

    # Returns a dict with (similarity_score, similarity_score_version, sampled_element_id)
    def score_frame(self, frame: LabeledFrame) -> SamplingScoreDict:

        # Guard on init and refine Optionals down
        if (
            self.pca is None
            or self.microclusters is None
            or self.microcluster_radii is None
            or self.microcluster_centroids is None
        ):
            raise Exception(
                "Attempted to score frame before loading sampling dataset information."
            )

        if not frame.embedding:
            raise Exception(
                "Frames for embedding distance sampling must have embeddings."
            )

        frame_with_embs = cast(GTFrameWithEmbeddings, frame)

        # List of {"uuid": ..., "embedding": ...} elements
        embeddings_to_score: List[FilteredEmbeddingShapeDict] = []
        frame_emb_vec = frame_with_embs.embedding.get("embedding")
        if self.element_type == "frame":
            if frame_emb_vec:
                embeddings_to_score = [
                    {
                        "uuid": frame_with_embs.embedding["task_id"],
                        "embedding": frame_emb_vec,
                    }
                ]
            else:
                raise Exception(
                    f"Frames for embedding distance sampling must have valid, non-empty frame embedding."
                )
        else:  # crop
            crop_embs = frame_with_embs._labels.crop_embeddings
            if crop_embs:
                embeddings_to_score = [e for e in crop_embs if e.get("embedding")]
            elif self.primary_task == "CLASSIFICATION":
                if frame_emb_vec:
                    # For projects with primary_task CLASSIFICATION, the element_type of all elements is mapped to "crop".
                    # However this is not apparent to the end user, who uploads their embeddings to the frame itself.
                    embeddings_to_score = [
                        {
                            "uuid": frame_with_embs.embedding["task_id"],
                            "embedding": frame_emb_vec,
                        }
                    ]
                else:
                    raise Exception(
                        "Valid, non-empty frame embeddings must be provided for CLASSIFICATION type issues."
                    )

        max_score = -1
        max_score_elt = None
        closest_microcluster_idx = None
        elt_embedding_vec = None

        for embedding_info in embeddings_to_score:
            element_id = embedding_info.get("uuid")
            raw_emb = embedding_info.get("embedding")

            wrapped = np.array([raw_emb])
            normalized = normalize(wrapped)
            vec = self.pca.transform(normalized)[0]

            for j in range(len(self.microclusters)):
                target_centroid = self.microcluster_centroids[j]
                dist = np.linalg.norm(vec - target_centroid)
                score = max(1 - dist / (2 * self.microcluster_radii[j]), 0)
                if score > max_score:
                    max_score = score
                    max_score_elt = element_id
                    closest_microcluster_idx = j
                    elt_embedding_vec = raw_emb

        return {
            "similarity_score": max_score,
            "similarity_score_version": "v1",
            "sampled_element_id": max_score_elt,
            "closest_microcluster_idx": closest_microcluster_idx,
            "elt_embedding_vec": elt_embedding_vec,
            "model_id": frame_with_embs.embedding.get("model_id"),
        }
