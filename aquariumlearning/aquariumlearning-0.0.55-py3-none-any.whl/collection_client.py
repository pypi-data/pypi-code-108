"""collection_client.py
============
The extended client module for collection campaigns.
"""

import os
import datetime
from random import random
import sys
import time
import uuid
import math
import json
import pandas as pd
from requests.packages.urllib3.util import retry
import pyarrow as pa
from uuid import uuid4
from io import IOBase
from tempfile import NamedTemporaryFile
from tqdm import tqdm
from google.resumable_media.requests import ChunkedDownload
from google.resumable_media.common import InvalidResponse, DataCorruption
from typing import (
    Any,
    Callable,
    Optional,
    Union,
    List,
    Dict,
    Tuple,
    IO,
    BinaryIO,
    TypeVar,
    Iterator,
)
from typing_extensions import Literal
from queue import PriorityQueue

from requests.adapters import prepend_scheme_if_needed

from .util import (
    requests_retry,
    raise_resp_exception_error,
    _is_one_gb_available,
    _upload_local_files,
    create_temp_directory,
    mark_temp_directory_complete,
    MAX_CHUNK_SIZE,
    MAX_FRAMES_PER_BATCH,
    DEFAULT_SAMPLING_THRESHOLD,
)
from .client import Client
from .dataset import LabeledDataset, LabeledFrame
from .inference import Inferences, InferencesFrame
from .sampling_agent import RandomSamplingAgent, SamplingScoreDict, SamplingAgent

from .embedding_distance_sampling import EmbeddingDistanceSamplingAgent

CollectionAssetType = Literal["sample_frame", "embedding"]
SortStatus = Literal["UNSORTED", "DISCARDED", "ACCEPTED"]
SimilarityResultProcessingStatus = Literal["ENQUEUED", "RUNNING", "DONE"]

DEFAULT_STATISTICS = {
    "n": 0,
    "min": float("inf"),
    "max": float("-inf"),
    "mean": 0,
    "variance": 0,
    "m2": 0,
}


class CollectionClient(Client):
    """Client class that interacts with the Aquarium REST API.
    Also handles extra work around collecting samples for collection campigns

    Args:
        api_endpoint (str, optional): The API endpoint to hit. Defaults to "https://illume.aquariumlearning.com/api/v1".
    """

    active_coll_camp_summaries: Dict[str, Any]  # Dictionary of campaign ID to summary
    camp_id_to_sample_agent: Dict[str, SamplingAgent]
    # TODO: This Any should be Optional[str], but the code doesn't currently handle it
    frame_batch_uuid_to_temp_file_path: Dict[str, Any]

    # TODO: I think it should be SamplingScoreDict?
    # frame_batch_uuid_to_camp_id_to_probability_score_info: Dict[str, Dict[str, List[SamplingScoreDict]]]
    frame_batch_uuid_to_camp_id_to_probability_score_info: Dict[
        str, Dict[str, List[Any]]
    ]
    camp_id_to_gcs_frame_urls: Dict[str, List[str]]
    camp_id_to_gcs_embedding_urls: Dict[str, List[str]]
    sampled_frame_statistics: Dict[str, Any]
    most_similar_frame: Optional[Dict[str, Any]]
    most_similar_frame_campaign_id: Optional[str]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.active_coll_camp_summaries = {}

        self.sampling_agent = EmbeddingDistanceSamplingAgent
        self.camp_id_to_sample_agent = {}

        self.frame_batch_uuid_to_temp_file_path = {}
        self.frame_batch_uuid_to_camp_id_to_probability_score_info = {}

        # A mapping of campaign ID to the list of GCS URLs (one URL per batch of frames)
        self.camp_id_to_gcs_frame_urls = {}
        self.camp_id_to_gcs_embedding_urls = {}

        self.temp_file_path = create_temp_directory()

        self.num_frames_processed = 0
        self.sampled_frame_statistics = DEFAULT_STATISTICS
        self.most_similar_frame = None
        self.most_similar_frame_campaign_id = None

    def _clear_cached_sample_state(self) -> None:
        self.frame_batch_uuid_to_temp_file_path = {}
        self.frame_batch_uuid_to_camp_id_to_probability_score_info = {}
        self.camp_id_to_gcs_frame_urls = {}
        self.num_frames_processed = 0
        self.camp_id_to_gcs_embedding_urls = {}
        self.sampled_frame_statistics = DEFAULT_STATISTICS
        self.most_similar_frame = None
        self.most_similar_frame_campaign_id = None

    def _campaign_str(self, campaign: Dict[str, Any]) -> str:
        return f"Collection Campaign (Issue {campaign.get('issue_uuid')}, version {campaign.get('issue_version')})"

    def _save_content_to_temp(
        self,
        file_name_prefix: str,
        writefunc: Callable[[IO[Any]], bool],
        mode: str = "w",
    ) -> Optional[str]:
        """saves whatever the write function wants to a temp file and returns the file path

        Args:
            file_name_prefix (str): prefix for the filename being saved
            writefunc ([filelike): function used to write data to the file opened

        Returns:
            str or None: path of file or none if nothing written
        """

        if not _is_one_gb_available():
            raise OSError(
                "Attempting to flush dataset to disk with less than 1 GB of available disk space. Exiting..."
            )

        data_rows_content = NamedTemporaryFile(
            mode=mode, delete=False, prefix=file_name_prefix, dir=self.temp_file_path
        )
        data_rows_content_path = data_rows_content.name
        success = writefunc(data_rows_content)

        data_rows_content.seek(0)
        data_rows_content.close()

        return data_rows_content_path if success else None

    def _write_frames_to_file(
        self, frames: List[Dict[str, Any]], filelike: IO[Any]
    ) -> bool:
        """Write the frame content to a text filelike object (File handle, StringIO, etc.)

        Args:
            filelike (filelike): The destination file-like to write to.
        Returns:
            bool indicating whether write was successful
        """
        for frame in frames:
            filelike.write(json.dumps(frame) + "\n")

        # Check if something was written
        return filelike.tell() != 0

    def _write_embeddings_to_file(
        self, embeddings: List[Dict[str, Any]], filelike: IO[Any]
    ) -> bool:
        """Write the embeddings to a text filelike object (File handle, StringIO, etc.)

        Args:
            embeddings (List[Dict[str, Any]]): Keys are "embedding" and "task_id"
            filelike (filelike): The destination file-like to write to.
        Returns:
            bool indicating whether write was successful
        """
        embeddings_as_dict = {
            "task_id": pd.Series([x["task_id"] for x in embeddings]),
            "embedding": pd.Series([x["embedding"] for x in embeddings]),
        }
        df = pd.DataFrame(embeddings_as_dict)
        indexed_df = df.set_index("task_id")
        if indexed_df is None:
            return False

        table = pa.Table.from_pandas(indexed_df)

        ipc_writer = pa.ipc.new_file(
            filelike.name, table.schema, use_legacy_format=False  # type: ignore
        )
        ipc_writer.write_table(table)  # type: ignore
        ipc_writer.close()

        return True

    def download_to_file(self, signed_url: str, filelike: IO[Any]) -> bool:
        xml_api_headers = {
            "content-type": "application/octet-stream",
        }
        download = ChunkedDownload(signed_url, MAX_CHUNK_SIZE, filelike)
        while not download.finished:
            try:
                download.consume_next_chunk(requests_retry)
            except (InvalidResponse, DataCorruption, ConnectionError):
                if download.invalid:
                    continue
                continue
        return True

    def get_unlabeled_results_for_issue(
        self,
        *,
        issue_uuid: str,
        unlabeled_dataset_name: Optional[str],
        sort_status: Optional[SortStatus] = "UNSORTED",
        unlabeled_only: Optional[bool] = True,
        retrigger_search: Optional[bool] = False,
    ) -> List[Dict[str, Any]]:
        """returns similar results from unlabeled dataset search

        Args:
            issue_uuid (str): the uuid of the seed issue
            unlabeled_dataset_name (str): the name of the unlabeled search dataset
            sort_status (Optional[SortStatus]): filter the returned collection frames by status (default UNSORTED)
            unlabeled_only (Optional[bool]): return only collection frames that haven't been sent to labeling
            retrigger_search (Optional[bool]): retrigger similarity search (NOTE: this only works for searches against unlabeled datasets. It will poll + wait for the result)

        Returns:
            List[Dict[str, Any]]: List of CollectionFrames for a given issue
        """

        if not unlabeled_dataset_name and retrigger_search:
            raise Exception(
                "Can't retrigger search for Python client collection campaigns, only campaigns against unlabeled datasets"
            )

        collection_campaigns = self._get_all_campaigns(target_issue_uuids=[issue_uuid])
        if not collection_campaigns:
            raise Exception(
                f"Issue {issue_uuid} does not support similarity search because it does not have an associated collection campaign."
            )

        campaign_id = collection_campaigns[0]["id"]
        project_name = collection_campaigns[0]["project_name"]

        if retrigger_search:
            print(f"Retriggering unlabeled similarity search for issue {issue_uuid}...")

            search_payload = {
                "search_dataset_name": unlabeled_dataset_name,
                "collection_campaign_id": campaign_id,
            }

            r = requests_retry.post(
                self.api_endpoint
                + f"/projects/{project_name}/issues/{issue_uuid}/find_similar_elements",
                headers=self._get_creds_headers(),
                json=search_payload,
            )
            raise_resp_exception_error(r)

            # TODO: possibly insert sleep in case status isn't set right away?

            retry_count = 0
            processing_status: SimilarityResultProcessingStatus = "ENQUEUED"
            while processing_status != "DONE":
                if retry_count != 0:
                    sleep_time = 2 ** retry_count
                    print(f"Still running. Sleeping for {sleep_time} seconds...")
                    time.sleep(sleep_time)

                print("Polling for search status...")
                polling_params = {"search_dataset_name": unlabeled_dataset_name}
                r = requests_retry.get(
                    self.api_endpoint
                    + f"/projects/{project_name}/issues/{issue_uuid}/similar_element_info",
                    headers=self._get_creds_headers(),
                    params=polling_params,
                )

                raise_resp_exception_error(r)
                poll_result: Dict[str, Any] = r.json()
                processing_status = poll_result["similar_elts_processing_status"]
                retry_count += 1

            print("Similarity search complete, fetching results...")

        fetch_params: Dict[str, Any] = {
            "unlabeled_only": unlabeled_only,
            "sort_status": sort_status,
            "python_client": True,
        }

        if unlabeled_dataset_name:
            fetch_params["search_dataset"] = unlabeled_dataset_name

        r = requests_retry.get(
            self.api_endpoint
            + f"/projects/{project_name}/collection_frames/for_issue/{issue_uuid}",
            headers=self._get_creds_headers(),
            params=fetch_params,
        )

        raise_resp_exception_error(r)
        result: List[Dict[str, Any]] = r.json()
        return result

    def _read_rows_from_disk(self, file_path: str) -> List[Dict[str, Any]]:
        """reads temp files from disk and loads the dicts in them into memory

        Args:
            file_path (str): file path to read from

        Returns:
            List[Dict[str, Any]]: List of LabeledFrames in a dict structure
        """
        with open(file_path, "r") as frame_file:
            return [json.loads(line.strip()) for line in frame_file.readlines()]

    def _get_all_campaigns(
        self, target_project_names: List[str] = [], target_issue_uuids: List[str] = []
    ) -> List[Dict[str, Any]]:
        """Gets all collection campaign summaries (filtered to the target_project_names if provided)

        Args:
            target_project_names (Optional[List[str]], optional): List of project names whose collection campaigns should be sampled for
            target_issue_uuids (Optional[List[str]], optional): List of issue uuids whose collection campaigns should be sampled for. This takes precedence over 'target_project_names' and is mutually exclusive.

        Returns:
            List[Dict[str, Any]]: List of dicts containing collection campaign summaries
        """
        params = {}
        if target_issue_uuids:
            params["target_issue_uuids"] = target_issue_uuids
        elif target_project_names:
            params["target_project_names"] = target_project_names

        r = requests_retry.get(
            self.api_endpoint + "/collection_campaigns/summaries",
            headers=self._get_creds_headers(),
            params=params,
        )

        raise_resp_exception_error(r)
        result: List[Dict[str, Any]] = r.json()
        return result

    def _upload_collection_assets_to_gcs(
        self,
        frame_batch_uuid: str,
        campaign_id: str,
        assets: Any,
        writefunc: Callable[[Any, IO[Any]], bool],
        asset_type: CollectionAssetType,
    ) -> List[str]:
        """takes frames for collection and posts it to the API in batches

        Args:
            frame_batch_uuid (str): The local frame batch these frames were sampled from
            campaign_id (str): The collection campaign id
            assets (Dict[str, Any]): Dict structure containing collection assets for a campaign to post
            asset_type (CollectionAssetType): The type of asset being uploaded
            writefunc ([Dict[str, Any], filelike]): function used to write data to the file opened
        Returns:
            List[str]: List of GCS URLs corresponding to the uploaded frame batches
        """

        T = TypeVar("T")

        def batches(lst: List[T], size: int) -> Iterator[List[T]]:
            for i in range(0, len(lst), size):
                yield lst[i : i + size]

        def save_batch(assets: List[Dict[str, Any]]) -> Optional[str]:
            current_time = datetime.datetime.now()
            # Write frames to local temp file
            temp_frame_prefix = "al_{}_{}s_{}_".format(
                current_time.strftime("%Y%m%d_%H%M%S_%f"), asset_type, frame_batch_uuid
            )
            temp_frame_path = self._save_content_to_temp(
                temp_frame_prefix,
                lambda x: writefunc([asset for asset in assets], x),
            )
            return temp_frame_path

        # Get upload / download URLs
        download_urls = []
        get_upload_path = (
            f"{self.api_endpoint}/collection_campaigns/{campaign_id}/get_upload_url"
        )

        batch_filepaths = [
            save_batch(batched_assets)
            for batched_assets in batches(assets, MAX_FRAMES_PER_BATCH)
        ]

        # TODO: Review, since this is a real code change. Do we expect these to ever
        # be falsey?
        successful_filepaths = [x for x in batch_filepaths if x]

        file_ext = ".jsonl" if asset_type == "sample_frame" else ".arrow"

        download_urls = _upload_local_files(
            successful_filepaths,
            get_upload_path,
            self._get_creds_headers(),
            f"{asset_type}s_{frame_batch_uuid}",
            file_ext,
            delete_after_upload=True,
        )

        return download_urls

    # TODO: Is it intentional to return something here?
    def _post_collection_frames(self, campaign: Dict[str, Any]) -> Any:
        """takes a payload and posts it to the API

        Args:
            payload (Dict[str, Any]): Dict structure containing the payload for a campaign to post
        """
        print(f"Saving collection frames for {self._campaign_str(campaign)}...")

        payload = {
            "collection_campaign_id": campaign["id"],
            "issue_uuid": campaign["issue_uuid"],
            "dataframe_urls": self.camp_id_to_gcs_frame_urls[campaign["id"]],
            "num_processed": self.num_frames_processed,
            "embedding_urls": self.camp_id_to_gcs_embedding_urls[campaign["id"]],
        }

        r = requests_retry.post(
            self.api_endpoint + "/projects/blah/collection_frames",
            headers=self._get_creds_headers(),
            json=payload,
        )

        raise_resp_exception_error(r)
        return r.json()

    def _is_postprocessing_complete(self, campaign_summary: Dict[str, Any]) -> bool:
        return bool(
            campaign_summary.get("pca_signed_url")
            and campaign_summary.get("microcluster_info_signed_url")
        )

    def sync_state(
        self, target_project_names: List[str] = [], target_issue_uuids: List[str] = []
    ) -> None:
        """Downloads all collection campaigns and preps sampler with sample frames

        Args:
            target_project_names (Optional[List[str]], optional): List of project names whose collection campaigns should be sampled for
            target_issue_uuids (Optional[List[str]], optional): List of issue uuids whose collection campaigns should be sampled for. This takes precedence over 'target_project_names' and is mutually exclusive.
        """
        print("Starting Sync")
        all_coll_camps = self._get_all_campaigns(
            target_project_names=target_project_names,
            target_issue_uuids=target_issue_uuids,
        )

        # Skip over collection campaigns that still need to be post-processed
        processing_coll_camps_issue_uuids = [
            c.get("issue_uuid")
            for c in all_coll_camps
            if c["active"] and not self._is_postprocessing_complete(c)
        ]
        if len(processing_coll_camps_issue_uuids) > 0:
            print(
                f"{len(processing_coll_camps_issue_uuids)} collection campaigns still awaiting postprocessing."
            )
            for issue_uuid in processing_coll_camps_issue_uuids:
                print(f" - issue uuid: {issue_uuid}")

        self.active_coll_camp_summaries = {
            c["id"]: c
            for c in all_coll_camps
            if c["active"] and self._is_postprocessing_complete(c)
        }
        print(
            f"Found {len(self.active_coll_camp_summaries)} Active Collection Campaigns"
        )

        # Initialize a sampling agent per active, postprocessed campaign
        self.camp_id_to_sample_agent = {
            c["id"]: self.sampling_agent()
            for c in self.active_coll_camp_summaries.values()
        }

        print(f"Downloading assets for each Collection Campaign")
        for campaign in self.active_coll_camp_summaries.values():
            # download each of the preprocessed files for the example dataset locally
            signed_urls = {
                "pca_signed_url": campaign.get("pca_signed_url"),
                "microcluster_info_signed_url": campaign.get(
                    "microcluster_info_signed_url"
                ),
            }

            url_key_to_downloaded_file_path: Dict[str, Optional[str]] = {}
            for url_key, signed_url in signed_urls.items():
                if signed_url is None:
                    url_key_to_downloaded_file_path[url_key] = None
                    continue
                current_time = datetime.datetime.now()
                random_uuid = str(uuid4())
                temp_file_prefix = "al_{}_{}_{}_{}".format(
                    current_time.strftime("%Y%m%d_%H%M%S_%f"),
                    str(campaign.get("id")),
                    url_key,
                    random_uuid,
                )
                file_path = self._save_content_to_temp(
                    temp_file_prefix,
                    lambda x: self.download_to_file(signed_url, x),
                    mode="wb",
                )
                url_key_to_downloaded_file_path[url_key] = file_path

            path_key_to_downloaded_file_path = {
                k[:-10] + "path": v for k, v in url_key_to_downloaded_file_path.items()
            }

            # Load data into agent for each campaign
            agent = self.camp_id_to_sample_agent[campaign.get("id")]
            agent.load_sampling_dataset(
                element_type=campaign.get("element_type"),
                preprocessed_info=path_key_to_downloaded_file_path,
                primary_task=campaign.get("primary_task"),
            )

    def sample_probabilities(self, frames: List[LabeledFrame]) -> Any:
        """Takes a list of Labeled Frames and stores scores for each based on each synced collection campaigns

        Args:
            frames (List[LabeledFrame]): a List of Labeled frames to score based on synced Collection Campaigns
        """
        print("Sampling frames...")

        batch_uuid = str(uuid4())
        self.frame_batch_uuid_to_camp_id_to_probability_score_info[batch_uuid] = {}

        for campaign in self.active_coll_camp_summaries.values():
            print(f"Scoring frames for {self._campaign_str(campaign)}...")
            self.frame_batch_uuid_to_camp_id_to_probability_score_info[batch_uuid][
                campaign["id"]
            ] = [
                # A dict with fields (similarity_score, similarity_score_version, sampled_element_id, closest_microcluster_idx)
                self.camp_id_to_sample_agent[campaign["id"]].score_frame(frame)
                for frame in tqdm(frames, desc="Num frames scored")
            ]

        current_time = datetime.datetime.now()
        temp_frame_prefix = "al_{}_collection_campaign_candidate_frames_{}_".format(
            current_time.strftime("%Y%m%d_%H%M%S_%f"), batch_uuid
        )

        frame_dicts = []
        for frame in frames:
            frame_dict = frame.to_dict()
            frame_dict["label_data"] = frame._labels.to_dict()["label_data"]
            frame_dicts.append(frame_dict)

        frame_path = self._save_content_to_temp(
            temp_frame_prefix,
            lambda x: self._write_frames_to_file(frame_dicts, x),
        )
        self.frame_batch_uuid_to_temp_file_path[batch_uuid] = frame_path

        print("Sampling complete!")

        self.num_frames_processed += len(frames)

        return self.frame_batch_uuid_to_camp_id_to_probability_score_info[batch_uuid]

    def _upload_frames_and_embeddings_for_campaign(
        self,
        frame_batch_uuid: str,
        campaign: Dict[str, Any],
        frames: List[Dict[str, Any]],
        embeddings: List[Dict[str, Any]],
    ) -> None:
        if len(frames) == 0:
            return

        print(f"Uploading Frames for {self._campaign_str(campaign)}")
        dataframe_urls = self._upload_collection_assets_to_gcs(
            frame_batch_uuid,
            campaign["id"],
            frames,
            self._write_frames_to_file,
            "sample_frame",
        )

        print(f"Uploading Embeddings for {self._campaign_str(campaign)}")
        embedding_urls = self._upload_collection_assets_to_gcs(
            frame_batch_uuid,
            campaign["id"],
            embeddings,
            self._write_embeddings_to_file,
            "embedding",
        )

        if campaign["id"] not in self.camp_id_to_gcs_frame_urls:
            self.camp_id_to_gcs_frame_urls[campaign["id"]] = dataframe_urls
            self.camp_id_to_gcs_embedding_urls[campaign["id"]] = embedding_urls
        else:
            self.camp_id_to_gcs_frame_urls[campaign["id"]].extend(dataframe_urls)
            self.camp_id_to_gcs_embedding_urls[campaign["id"]].extend(embedding_urls)

    # Based on Welford's algorithm for updating mean + variance
    def _update_frame_statistics(self, similarity_score: float) -> None:
        self.sampled_frame_statistics["n"] += 1

        delta = similarity_score - self.sampled_frame_statistics["mean"]
        self.sampled_frame_statistics["mean"] += (
            delta / self.sampled_frame_statistics["n"]
        )
        delta2 = similarity_score - self.sampled_frame_statistics["mean"]
        self.sampled_frame_statistics["m2"] += delta * delta2
        self.sampled_frame_statistics["variance"] = (
            self.sampled_frame_statistics["m2"] / self.sampled_frame_statistics["n"]
        )

        if similarity_score < self.sampled_frame_statistics["min"]:
            self.sampled_frame_statistics["min"] = similarity_score
        if similarity_score > self.sampled_frame_statistics["max"]:
            self.sampled_frame_statistics["max"] = similarity_score

    def _save_for_collection_with_threshold(
        self, override_sampling_threshold: float = None, dry_run: bool = False
    ) -> None:
        num_frame_batches = len(self.frame_batch_uuid_to_temp_file_path)

        for idx, frame_batch_uuid in enumerate(
            self.frame_batch_uuid_to_temp_file_path.keys()
        ):
            print(f"Processing frame batch {idx + 1} of {num_frame_batches}...")

            frames = self._read_rows_from_disk(
                self.frame_batch_uuid_to_temp_file_path[frame_batch_uuid]
            )
            camp_id_to_probability_score_info = (
                self.frame_batch_uuid_to_camp_id_to_probability_score_info[
                    frame_batch_uuid
                ]
            )
            for campaign in self.active_coll_camp_summaries.values():
                scores = camp_id_to_probability_score_info[campaign["id"]]
                sampling_threshold = (
                    DEFAULT_SAMPLING_THRESHOLD
                    if campaign.get("sampling_threshold") is None
                    else campaign.get("sampling_threshold")
                )
                sampling_threshold = (
                    sampling_threshold
                    if override_sampling_threshold is None
                    else override_sampling_threshold
                )
                filtered_frame_indexes_and_scores = filter(
                    lambda score: score[1].get("similarity_score")
                    >= sampling_threshold,
                    enumerate(scores),
                )
                filtered_frame_indexes = map(
                    lambda score: score[0], filtered_frame_indexes_and_scores
                )

                filtered_frames_dict = []
                sample_embeddings: List[Dict[str, Any]] = []
                for idx in filtered_frame_indexes:
                    frame_dict = frames[idx]
                    # Add info from scoring (e.g. similarity score)
                    frame_dict["similarity_score"] = scores[idx].get("similarity_score")
                    frame_dict["sampled_element_id"] = scores[idx].get(
                        "sampled_element_id"
                    )
                    frame_dict["similarity_score_version"] = scores[idx].get(
                        "similarity_score_version"
                    )
                    frame_dict["closest_microcluster_idx"] = scores[idx].get(
                        "closest_microcluster_idx"
                    )
                    frame_dict["model_id"] = scores[idx].get("model_id")

                    filtered_frames_dict.append(frame_dict)
                    sample_embeddings.append(
                        {
                            "task_id": frame_dict.get("task_id"),
                            "embedding": scores[idx].get("elt_embedding_vec"),
                        }
                    )

                    # Update aggregate statistics
                    if (
                        frame_dict["similarity_score"]
                        > self.sampled_frame_statistics["max"]
                    ):
                        self.most_similar_frame = frame_dict
                        self.most_similar_frame_campaign_id = campaign["id"]
                    self._update_frame_statistics(frame_dict["similarity_score"])

                if not dry_run:
                    self._upload_frames_and_embeddings_for_campaign(
                        frame_batch_uuid,
                        campaign,
                        filtered_frames_dict,
                        sample_embeddings,
                    )

    def _save_for_collection_with_count(
        self, target_sample_count: int, dry_run: bool = False
    ) -> None:
        print(f"Targeting sample frame count of {target_sample_count}...")

        # If we're targeting a specific frame count, keep a global queue across batches
        # The extra slot allows us to determine what to keep when the queue reaches target_sample_count
        frame_queue: "PriorityQueue[Tuple[float, str, str, Dict[str, Any], List[float]]]" = PriorityQueue(
            target_sample_count + 1
        )

        with tqdm(
            total=self.num_frames_processed,
            file=sys.stdout,
            unit_scale=True,
            desc="Frame Processing Progress",
        ) as pbar:  # type: tqdm[Any]
            for idx, frame_batch_uuid in enumerate(
                self.frame_batch_uuid_to_temp_file_path.keys()
            ):
                frames = self._read_rows_from_disk(
                    self.frame_batch_uuid_to_temp_file_path[frame_batch_uuid]
                )
                camp_id_to_probability_score_info = (
                    self.frame_batch_uuid_to_camp_id_to_probability_score_info[
                        frame_batch_uuid
                    ]
                )

                for frame_idx, frame in enumerate(frames):
                    max_score_embedding: List[float] = []
                    max_score_campaign_id: str = ""
                    max_similarity_score: float = -1

                    # Determine which campaign this frame is the best match for
                    for campaign in self.active_coll_camp_summaries.values():
                        score_info = camp_id_to_probability_score_info[campaign["id"]][
                            frame_idx
                        ]
                        if score_info.get("similarity_score") > max_similarity_score:
                            max_similarity_score = score_info.get("similarity_score")
                            max_score_campaign_id = campaign["id"]
                            # Extract the matching embedding info
                            max_score_embedding = score_info.get("elt_embedding_vec")
                            score_info = {
                                k: v
                                for k, v in score_info.items()
                                if k != "elt_embedding_vec"
                            }
                            # Then merge score_info into the frame_dict
                            frame.update(score_info)

                    # No matching embedding was found for this frame
                    # (e.g. frame itself might not have embeddings)
                    if frame.get("sampled_element_id") is None:
                        pbar.update(1)
                        continue

                    frame_task_id: str = frame["task_id"]
                    frame_queue.put(
                        (
                            max_similarity_score,
                            frame_task_id,  # To help with uniqueness/sorting
                            max_score_campaign_id,
                            frame,
                            max_score_embedding,
                        )
                    )

                    # If frame queue is full, we need to remove the lowest to keep room open for sorting the next entry
                    if frame_queue.full():
                        frame_queue.get()

                    pbar.update(1)

        campaign_id_to_frames: Dict[str, List[Dict[str, Any]]] = {
            campaign["id"]: [] for campaign in self.active_coll_camp_summaries.values()
        }
        campaign_id_to_embeddings: Dict[str, List[Dict[str, Any]]] = {
            campaign["id"]: [] for campaign in self.active_coll_camp_summaries.values()
        }

        while not frame_queue.empty():
            score, task_id, campaign_id, frame_dict, embedding = frame_queue.get()

            # Update aggregate statistics
            if frame_dict["similarity_score"] > self.sampled_frame_statistics["max"]:
                self.most_similar_frame = frame_dict
                self.most_similar_frame_campaign_id = campaign_id

            self._update_frame_statistics(frame_dict["similarity_score"])

            campaign_id_to_frames[campaign_id].append(frame_dict)
            campaign_id_to_embeddings[campaign_id].append(
                {
                    "task_id": task_id,
                    "embedding": embedding,
                }
            )

        if not dry_run:
            # We need a filler uuid (since we're not uploading by frame batch)
            filler_uuid = str(uuid4())
            for campaign in self.active_coll_camp_summaries.values():
                self._upload_frames_and_embeddings_for_campaign(
                    filler_uuid,
                    campaign,
                    campaign_id_to_frames[campaign["id"]],
                    campaign_id_to_embeddings[campaign["id"]],
                )

    def _report_sampled_frame_statistics(self) -> None:
        print("===================")
        print("Stats Summary for Sampled Frames")
        print("===================")
        print(
            f"- Num collected samples / total num frames seen: {self.sampled_frame_statistics['n']} / {self.num_frames_processed}"
        )
        print(f"- Min similarity score: {self.sampled_frame_statistics['min']:.3f}")
        print(f"- Max similarity score: {self.sampled_frame_statistics['max']:.3f}")
        print(f"- Mean similarity score: {self.sampled_frame_statistics['mean']:.3f}")
        print(
            f"- Standard deviation similarity score: {math.sqrt(self.sampled_frame_statistics['variance']):.3f}\n"
        )

    def save_for_collection(
        self,
        override_sampling_threshold: float = None,
        target_sample_count: int = None,
        dry_run: bool = False,
    ) -> None:
        """Based on the sampling threshold, take all sampled frames and upload those that score above
        the sampling threshold for each Collection Campaign.

        Args:
            override_sampling_threshold (float, optional): Override sampling threshold for all campaigns to save to server. If this value is set it will not use the sampling threshold set in UI for each Collection Campaign.
            target_sample_count(int, optional): Instead of collecting all samples above a specified similarity threshold, you can specify this option to save the N most similar samples.
        """

        if dry_run:
            print("===================")
            print("DRY RUN: No collection frames will be uploaded.")
            print("===================")

        # First determine which frames/embeddings to save and upload to GCS
        if target_sample_count is not None:
            self._save_for_collection_with_count(target_sample_count, dry_run=dry_run)
        else:
            self._save_for_collection_with_threshold(
                override_sampling_threshold, dry_run=dry_run
            )

        self._report_sampled_frame_statistics()

        if dry_run:
            if (
                self.most_similar_frame_campaign_id is not None
                and self.most_similar_frame is not None
            ):
                print("===================")
                print("Preview Frame")
                print("===================")
                print("Generating preview frame for highest scoring sample...")
                print(
                    f"Similarity score: {self.most_similar_frame['similarity_score']:.3f}\n"
                )
                # Preview first frame
                preview_frame_campaign: Dict[
                    str, Any
                ] = self.active_coll_camp_summaries[self.most_similar_frame_campaign_id]

                self._preview_frame_dict(
                    project_id=preview_frame_campaign["project_name"],
                    both_frames_dict={
                        "labeled_frame": self.most_similar_frame,
                        "inference_frame": None,
                    },
                    selected_label=self.most_similar_frame["sampled_element_id"]
                    if preview_frame_campaign["element_type"] == "crop"
                    else None,
                )
        else:
            # Now create the collection frames in the DB
            for campaign in self.active_coll_camp_summaries.values():
                if campaign["id"] in self.camp_id_to_gcs_frame_urls:
                    resp = self._post_collection_frames(campaign)
                    print(
                        "Successfully saved {} new frames for {} ({} frames already referenced by existing samples)".format(
                            resp.get("num_new_frames"),
                            self._campaign_str(campaign),
                            resp.get("num_duplicate_frames"),
                        )
                    )
                else:
                    print(f"No samples matched for {self._campaign_str(campaign)}")

            mark_temp_directory_complete(self.temp_file_path)
            self._clear_cached_sample_state()
