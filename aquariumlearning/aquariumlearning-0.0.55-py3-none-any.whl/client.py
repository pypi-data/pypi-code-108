"""client.py
============
The main client module.
"""

import os
import datetime
import json
import time
from requests.exceptions import ConnectionError
from uuid import uuid4
from io import BytesIO
from google.resumable_media.requests import ResumableUpload
from google.resumable_media.common import InvalidResponse, DataCorruption
from tqdm import tqdm
import sys
from .frames import UserMetadataEntry
from .viridis import viridis_rgb as viridis_rgb
from .turbo import turbo_rgb as turbo_rgb
from .issues import IssueManager as IssueManager
from .metrics_manager import MetricsManager as MetricsManager
from .datasharing import (
    check_urls as check_urls,
    get_mode as get_mode,
    get_errors as get_errors,
)
import re
from typing import Any, Optional, Union, List, Dict, Tuple, Iterable, Callable, cast
from typing_extensions import TypedDict

from .util import (
    BaseLabelEntryDict,
    _upload_local_files,
    requests_retry,
    assert_valid_name,
    MAX_CHUNK_SIZE,
    raise_resp_exception_error,
    maybe_parse_json_vals,
    split_user_attrs,
    USER_METADATA_SEQUENCE,
)

# All imports here necessary for referenceing and compatiblity
from .dataset import LabeledDataset as LabeledDataset, LabeledFrame as LabeledFrame
from .inference import Inferences as Inferences, InferencesFrame as InferencesFrame
from .frames import UpdateFrame
from .labels import (
    UpdateGTLabelSet,
    UpdateInferenceLabelSet,
)
from .class_map import (
    LabelClassMap as LabelClassMap,
    ClassMapEntry as ClassMapEntry,
    ClassMapUpdateEntry as ClassMapUpdateEntry,
    tableau_colors as tableau_colors,
    orig_label_color_list as orig_label_color_list,
)


class StratifiedMetricsDict(TypedDict):
    name: str
    ordered_values: List[str]


class StratifiedMetricsDefinition:
    """Definitions for stratified metrics given object-level attributes

    Args:
        name (str): The name of this attribute, which should match the attribute on object labels.
        ordered_values (List[str]): The ordered list of valid values to group by.
    """

    def __init__(self, name: str, ordered_values: Iterable[str]) -> None:
        self.name = name
        self.ordered_values = list(ordered_values)  # In case it's a tuple

    def to_dict(self) -> StratifiedMetricsDict:
        return {"name": self.name, "ordered_values": self.ordered_values}


class CustomMetricsDefinition:
    """Definitions for custom user provided metrics.

    Args:
        name (str): The name of this metric.
        metrics_type (str): The metrics type, either 'objective' or 'confusion_matrix'.
    """

    # TODO: Make these literal types too in the type system?
    OBJECTIVE = "objective"
    CONFUSION_MATRIX = "confusion_matrix"

    def __init__(self, name: str, metrics_type: str) -> None:
        valid_metrics_types = set(["objective", "confusion_matrix"])
        self.name = name
        self.metrics_type = metrics_type

    def to_dict(self) -> Dict[str, str]:
        return {"name": self.name, "metrics_type": self.metrics_type}


class Client:
    """Client class that interacts with the Aquarium REST API.

    Args:
        api_endpoint (str, optional): The API endpoint to hit. Defaults to "https://illume.aquariumlearning.com/api/v1".
    """

    _creds_token: Optional[str]
    _creds_app_id: Optional[str]
    _creds_app_key: Optional[str]
    _creds_api_key: Optional[str]
    api_endpoint: str

    def __init__(
        self,
        *,
        api_endpoint: str = "https://illume.aquariumlearning.com/api/v1",
        **kwargs: Any,
    ) -> None:
        self._creds_token = None
        self._creds_app_id = None
        self._creds_app_key = None
        self._creds_api_key = None
        self.api_endpoint = api_endpoint

    def _get_creds_headers(self) -> Dict[str, str]:
        """Get appropriate request headers for the currently set credentials.

        Raises:
            Exception: No credentials set.

        Returns:
            dict: Dictionary of headers
        """
        if self._creds_token:
            return {"Authorization": "Bearer {token}".format(token=self._creds_token)}
        elif self._creds_api_key:
            return {"x-illume-api-key": self._creds_api_key}
        elif self._creds_app_id and self._creds_app_key:
            return {
                "x-illume-app": self._creds_app_id,
                "x-illume-key": self._creds_app_key,
            }
        else:
            raise Exception("No credentials set.")

    def set_credentials(
        self,
        *,
        token: Optional[str] = None,
        app_id: Optional[str] = None,
        app_key: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        """Set credentials for the client.

        Args:
            api_key (str, optional): A string for a long lived API key. Defaults to None.
            token (str, optional): A JWT providing auth credentials. Defaults to None.
            app_id (str, optional): Application ID string. Defaults to None.
            app_key (str, optional): Application secret key. Defaults to None.

        Raises:
            Exception: Invalid credential combination provided.
        """
        if api_key is not None:
            self._creds_api_key = api_key
        elif token is not None:
            self._creds_token = token
        elif app_id is not None and app_key is not None:
            self._creds_app_id = app_id
            self._creds_app_key = app_key
        else:
            raise Exception(
                "Please provide either an api_key, token, or app_id and app_key"
            )

    def _format_error_logs(self, raw_error_logs: List[Dict[str, str]]) -> List[str]:
        """Format error log data into strings.

        Args:
            raw_error_logs (list[dict]): Error log data.

        Returns:
            list[str]: list of string formatted error messages.
        """
        formatted_lines = []
        for raw in raw_error_logs:
            formatted_lines.append(
                f"    {raw.get('aquarium_dataflow_step', '')}: {raw.get('msg', '')}"
            )
        return formatted_lines

    def get_issue_manager(self, project_id: str) -> IssueManager:
        """Get an issue manager object.

        Args:
            project_id (str): Project ID to manage.

        Returns:
            IssueManager: The issue manager object.
        """
        return IssueManager(self, project_id)

    def get_metrics_manager(self, project_id: str) -> MetricsManager:
        """Get a metrics manager object.

        Args:
            project_id (str): Project ID to manage.

        Returns:
            MetricsManager: The metrics manager object.
        """
        return MetricsManager(self, project_id)

    def get_projects(self) -> List[Dict[str, Any]]:
        """Get info about existing projects

        Returns:
            list of dict: Project Info
        """
        r = requests_retry.get(
            self.api_endpoint + "/projects", headers=self._get_creds_headers()
        )

        raise_resp_exception_error(r)
        result: List[Dict[str, Any]] = r.json()
        return result

    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get detailed info about a specific project

        Returns:
            Dict[str, Any]: detailed info about a project
        """
        r = requests_retry.get(
            self.api_endpoint + "/projects/" + project_id,
            headers=self._get_creds_headers(),
        )

        raise_resp_exception_error(r)
        result: Dict[str, Any] = r.json()
        return result

    def delete_project(self, project_id: str) -> None:
        """Mark a project for deletion

        Args:
            project_id (str): project_id
        """
        if not self.project_exists(project_id):
            raise Exception("Project {} does not exist.".format(project_id))

        url = self.api_endpoint + "/projects/{}".format(project_id)
        r = requests_retry.delete(url, headers=self._get_creds_headers())

        raise_resp_exception_error(r)

    def project_exists(self, project_id: str) -> bool:
        """Checks whether a project exists.

        Args:
            project_id (str): project_id

        Returns:
            bool: Does project exist
        """
        projects = self.get_projects()
        existing_project_ids = [project["id"] for project in projects]
        return project_id in existing_project_ids

    def create_project(
        self,
        project_id: str,
        label_class_map: LabelClassMap,
        primary_task: Optional[str] = None,
        secondary_labels: Optional[Any] = None,
        frame_links: Optional[List[str]] = None,
        label_links: Optional[List[str]] = None,
        default_camera_target: Optional[List[float]] = None,
        default_camera_position: Optional[List[float]] = None,
        custom_metrics: Optional[
            Union[CustomMetricsDefinition, List[CustomMetricsDefinition]]
        ] = None,
        max_shown_categories: Optional[int] = None,
        stratified_metrics: Optional[List[StratifiedMetricsDefinition]] = None,
        include_no_gt: Optional[bool] = None,
        metrics_confidence_threshold: Optional[float] = None,
        metrics_iou_threshold: Optional[float] = None,
        external_metadata: Optional[Dict[str, Any]] = None,
        binary_classification_negative_class: Optional[str] = None,
    ) -> None:
        """Create a new project via the REST API.

        Args:
            project_id (str): project_id
            label_class_map (LabelClassMap): The label class map used to interpret classifications.
            primary_task (Optional[str], optional): Any specific primary task for a non-object detection or classification task. Can be '2D_SEMSEG' or '2D_INSTANCE_SEGMENTATION' or 'CLASSIFICATION' or 'CLASSIFICATION_WITH_GEOMETRY' or 'BINARY_CLASSIFiCATION' or None.
            secondary_labels ([type], optional): List of secondary labels in classification tasks
            frame_links (Optional[List[str]], optional): List of string keys for links between frames
            label_links (Optional[List[str]], optional): List of string keys for links between labels
            default_camera_target (Optional[List[float]], optional): For 3D scenes, the default camera target
            default_camera_position (Optional[List[float]], optional): For 3D scenes, the default camera position
            custom_metrics (Optional[ Union[CustomMetricsDefinition, List[CustomMetricsDefinition]] ], optional): Defines which custom metrics exist for this project, defaults to None.
            max_shown_categories (Optional[int], optional): For categorical visualizations, set the maximum shown simultaneously. Max 100.
            stratified_metrics (Optional[List[StratifiedMetricsDefinition]], optional): Defines what object-level attributes to stratify metrics over.
            metrics_confidence_threshold (Optional[float], optional): In order to calculate metrics + confusion matrices, Aquarium uses this threshold (in combination with IOU) to match your ground truth (GT) labels with your inference labels. Defaults to 0.1 if not specified.
            metrics_iou_threshold(Optional[float], optional): In order to calculate metrics + confusion matrices, Aquarium uses this threshold (in combination with confidence) to match your ground truth (GT) labels with your inference labels. Defaults to 0.5 if not specified.
            external_metadata (Optional[Dict[str, Any]], optional): A JSON object that can be used to attach metadata to the project itself
            binary_classification_negative_class (Optional[str]): Required when primary_task is 'BINARY_CLASSIFiCATION'. The name of the negative class.
        """

        assert_valid_name(project_id)

        if not isinstance(label_class_map, LabelClassMap):
            raise Exception("label_class_map must be a LabelClassMap")

        if not label_class_map.entries:
            raise Exception("label_class_map must have at least one class")

        dumped_classmap = [x.to_dict() for x in label_class_map.entries]
        payload = {"project_id": project_id, "label_class_map": dumped_classmap}

        if primary_task is not None:
            payload["primary_task"] = primary_task
            if primary_task == "BINARY_CLASSIFICATION":
                if binary_classification_negative_class is None:
                    raise Exception(
                        "Must specify negative class for binary classification"
                    )
                if len(label_class_map.entries) != 2:
                    raise Exception(
                        "Binary classification tasks must have exactly two classes"
                    )
                if (
                    len(
                        [
                            x
                            for x in label_class_map.entries
                            if x.name == binary_classification_negative_class
                        ]
                    )
                    != 1
                ):
                    raise Exception("Negative class must be in classmap")
                payload[
                    "binary_classification_negative_class"
                ] = binary_classification_negative_class

        if secondary_labels is not None:
            dumped_secondary_labels = []
            for raw in secondary_labels:
                dumped_classmap = [x.to_dict() for x in raw["label_class_map"].entries]
                raw["label_class_map"] = dumped_classmap
                dumped_secondary_labels.append(raw)

            payload["secondary_labels"] = dumped_secondary_labels
        if frame_links is not None:
            if not isinstance(frame_links, list):
                raise Exception("frame_links must be a list of strings")
            payload["frame_links"] = frame_links
        if label_links is not None:
            if not isinstance(label_links, list):
                raise Exception("label_links must be a list of strings")
            payload["label_links"] = label_links
        if default_camera_position is not None:
            if not isinstance(default_camera_position, list):
                raise Exception("default_camera_position must be a list of floats")
            payload["default_camera_position"] = default_camera_position
        if default_camera_target is not None:
            if not isinstance(default_camera_target, list):
                raise Exception("default_camera_target must be a list of floats")
            payload["default_camera_target"] = default_camera_target
        if custom_metrics is not None:
            if isinstance(custom_metrics, CustomMetricsDefinition):
                custom_metrics = [custom_metrics]

            if (
                not custom_metrics
                or (not isinstance(custom_metrics, list))
                or (not isinstance(custom_metrics[0], CustomMetricsDefinition))
            ):
                raise Exception(
                    "custom_metrics must be a CustomMetricsDefinition or list of CustomMetricsDefinition."
                )

            serializable_custom = [x.to_dict() for x in custom_metrics]
            payload["custom_metrics"] = serializable_custom

        if stratified_metrics is not None:
            if (
                not stratified_metrics
                or (not isinstance(stratified_metrics, list))
                or (not isinstance(stratified_metrics[0], StratifiedMetricsDefinition))
            ):
                raise Exception(
                    "stratified_metrics must be a list of StratifiedMetricsDefinition."
                )
            serializable_strat = [x.to_dict() for x in stratified_metrics]
            payload["stratified_metrics"] = serializable_strat

        if max_shown_categories is not None:
            if not isinstance(max_shown_categories, int):
                raise Exception("max_shown_categories must be an int")
            if max_shown_categories < 1 or max_shown_categories > 100:
                raise Exception("max_shown_categories must be between 1 and 100")
            payload["max_shown_categories"] = max_shown_categories

        if include_no_gt is not None:
            payload["include_no_gt"] = include_no_gt

        if metrics_confidence_threshold is not None:
            if not isinstance(metrics_confidence_threshold, float):
                raise Exception("metrics_confidence_threshold must be a float")
            payload["confidence_threshold"] = metrics_confidence_threshold

        if metrics_iou_threshold is not None:
            if not isinstance(metrics_iou_threshold, float):
                raise Exception("metrics_iou_threshold must be a float")
            payload["iou_threshold"] = metrics_iou_threshold

        if external_metadata is not None:
            if not isinstance(external_metadata, dict) or (
                external_metadata and not isinstance(next(iter(external_metadata)), str)
            ):
                raise Exception("external_metadata must be a dict with string keys")
            payload["external_metadata"] = external_metadata

        r = requests_retry.post(
            self.api_endpoint + "/projects",
            headers=self._get_creds_headers(),
            json=payload,
        )
        raise_resp_exception_error(r)

    def _preview_frame_dict(
        self,
        project_id: str,
        both_frames_dict: Dict[str, Optional[Dict[str, Any]]],
        selected_label: Optional[str] = None,
    ) -> None:
        """Generate preview with both dataset frame and inference frame as dict

        Args:
            project_id (str): name of project to preview frame with
            both_frames_dict (dict): Dictionary containing the labeled and inference frame
        """
        api_path = "/projects/{}/preview_frame".format(project_id)

        preview_frame_api_root = self.api_endpoint + api_path

        r = requests_retry.post(
            preview_frame_api_root,
            headers=self._get_creds_headers(),
            json=both_frames_dict,
        )
        response_data = r.json()
        if response_data.get("preview_frame_uuid"):
            print("Please visit the following url to preview your frame in the webapp")
            url = (
                self.api_endpoint[:-7]
                + api_path
                + "/"
                + response_data["preview_frame_uuid"]
            )
            if selected_label is not None:
                url += f"?selectedLabel={selected_label}"
            print(f"{url}\n")
        else:
            raise Exception(
                "Preview URL could not be constructed by server. "
                "Please make sure you're logged in and check frame data accordingly."
            )

    def preview_frame(
        self,
        project_id: str,
        labeled_frame: LabeledFrame,
        inference_frame: Optional[InferencesFrame] = None,
    ) -> None:
        """prints out a URL that lets you preview a provided frame in the web browser
        Useful for debugging data and image url issues.

        Args:
            project_id (str): Name of project to be associated for this frame preview (for label class association)
            labeled_frame (LabeledFrame): Labeled Frame desired for preview in web-app
            inference_frame (Optional[InferencesFrame], optional): Labeled Inference Desired for preview in web-app. Defaults to None.
        """

        both_frames: Dict[str, Optional[Dict[str, Any]]] = {}
        labeled_frame_dict = labeled_frame.to_dict()
        labeled_frame_dict["label_data"] = labeled_frame._labels.to_dict()["label_data"]
        both_frames["labeled_frame"] = labeled_frame_dict
        both_frames["inference_frame"] = (
            inference_frame.to_dict() if inference_frame else None
        )
        self._preview_frame_dict(project_id, both_frames)

    def update_project_metadata(
        self, project_id: str, external_metadata: Dict[str, Any]
    ) -> None:
        """Update project metadata

        Args:
            project_id (str): The project id.
            external_metadata (Dict[Any, Any]): The new metadata
        """
        if not isinstance(external_metadata, dict) or (
            external_metadata and not isinstance(next(iter(external_metadata)), str)
        ):
            raise Exception("external_metadata must be a dict with string keys")

        payload = {"external_metadata": external_metadata}
        r = requests_retry.post(
            f"{self.api_endpoint}/projects/{project_id}/metadata",
            headers=self._get_creds_headers(),
            json=payload,
        )
        raise_resp_exception_error(r)

    def update_label_class_map_colors(
        self, project_id: str, changed_label_classes: List[ClassMapUpdateEntry]
    ) -> None:
        """Updates label class colors of a specific project

        Args:
            project_id (str): The project id.
            changed_label_classes (List[ClassMapUpdateEntry]): The list of label classes with changed colors. Must be a subset of the project's overall label class map
        """
        project = self.get_project(project_id)
        label_class_map_dict_by_id = {
            label_class["id"]: label_class for label_class in project["label_class_map"]
        }
        label_class_map_dict_by_name = {
            label_class["name"]: label_class
            for label_class in project["label_class_map"]
        }

        seen_ids = set()
        dumped_changes = []
        for entry in changed_label_classes:
            if not entry.class_id:
                known_label_class = label_class_map_dict_by_name.get(entry.name)
                if not known_label_class:
                    raise Exception(
                        f"Label class with name {entry.name} could not be found in the project's label class map. "
                        "This method only allows changing an existing label class map. "
                        "To append new label classes please use create_project."
                    )
                entry.class_id = known_label_class["id"]

            known_label_class = label_class_map_dict_by_id.get(entry.class_id)

            if not known_label_class:
                raise Exception(
                    f"Label class with id {entry.class_id} could not be found in the project's label class map. "
                    "This method only allows changing an existing label class map. "
                    "To append new label classes please use create_project."
                )

            if entry.class_id in seen_ids:
                raise Exception(
                    f"Label class with id {entry.class_id} ({known_label_class['name']}) has multiple change entries. "
                    "Please consolidate into one change."
                )

            seen_ids.add(entry.class_id)
            dumped_entry = entry.to_dict()

            # lazy shallow None check to avoid overwriting with a null
            dumped_patch_entry = {
                k: v for k, v in dumped_entry.items() if v is not None
            }

            dumped_changes.append(dumped_patch_entry)

        payload = {"label_class_map": dumped_changes}
        r = requests_retry.patch(
            f"{self.api_endpoint}/projects/{project_id}/label_class_map",
            headers=self._get_creds_headers(),
            json=payload,
        )
        raise_resp_exception_error(r)

    def get_datasets(
        self, project_id: str, include_archived: Optional[bool]
    ) -> List[Dict[str, Any]]:
        """Get existing datasets for a project.

        Args:
            project_id (str): The project id.

        Returns:
            list: A list of dataset info for the project.
        """
        datasets_api_root = self.api_endpoint + "/projects/{}/datasets".format(
            project_id
        )
        params = {"include_archived": include_archived} if include_archived else {}
        r = requests_retry.get(
            datasets_api_root, headers=self._get_creds_headers(), params=params
        )
        raise_resp_exception_error(r)
        result: List[Dict[str, Any]] = r.json()
        return result

    def get_dataset(self, project_id: str, dataset_id: str) -> Dict[str, Any]:
        """Get existing dataset for a project.

        Args:
            project_id (str): The project id.
            dataset_id (str): dataset_id

        Returns:
            dict: The dataset info.
        """
        url = self.api_endpoint + "/projects/{}/datasets/{}".format(
            project_id, dataset_id
        )
        r = requests_retry.get(url, headers=self._get_creds_headers())
        raise_resp_exception_error(r)
        result: Dict[str, Any] = r.json()
        return result

    def delete_dataset(self, project_id: str, dataset_id: str) -> None:
        """Mark a dataset for deletion

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id
        """
        if not self.dataset_exists(project_id, dataset_id):
            raise Exception("Dataset {} does not exist.".format(dataset_id))

        url = self.api_endpoint + "/projects/{}/datasets/{}".format(
            project_id, dataset_id
        )
        r = requests_retry.delete(url, headers=self._get_creds_headers())

        raise_resp_exception_error(r)

    def dataset_exists(self, project_id: str, dataset_id: str) -> bool:
        """Check if a dataset exists.

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id

        Returns:
            bool: Whether the dataset already exists.
        """
        datasets = self.get_datasets(project_id, include_archived=True)
        existing_dataset_ids = [dataset.get("id") for dataset in datasets]
        return dataset_id in existing_dataset_ids

    def is_dataset_processed(self, project_id: str, dataset_id: str) -> bool:
        """Check if a dataset is fully processed.

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id

        Returns:
            bool: If the dataset is done processing.
        """
        endpoint_path = (
            self.api_endpoint
            + "/projects/{}/datasets/{}/is_processed".format(project_id, dataset_id)
        )

        r = requests_retry.get(endpoint_path, headers=self._get_creds_headers())
        raise_resp_exception_error(r)
        parsed: Dict[str, bool] = r.json()
        return parsed["processed"]

    def is_dataset_archived(self, project_id: str, dataset_id: str) -> bool:
        """Check if a dataset has been archived.

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id

        Returns:
            bool: If the dataset is archived. Returns False if dataset does not exist
        """
        endpoint_path = (
            self.api_endpoint
            + "/projects/{}/datasets/{}/is_archived".format(project_id, dataset_id)
        )

        r = requests_retry.get(endpoint_path, headers=self._get_creds_headers())
        raise_resp_exception_error(r)
        parsed: Dict[str, bool] = r.json()
        return parsed["archived"]

    def get_dataset_ingest_error_logs(
        self, project_id: str, dataset_id: str
    ) -> List[Dict[str, Any]]:
        """Get ingest error log entries for a dataset.

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id

        Returns:
            list[dict]: List of error entries
        """
        endpoint_path = (
            self.api_endpoint
            + "/projects/{}/datasets/{}/ingest_error_logs".format(
                project_id, dataset_id
            )
        )

        r = requests_retry.get(endpoint_path, headers=self._get_creds_headers())
        raise_resp_exception_error(r)
        parsed: List[Dict[str, Any]] = r.json()
        return parsed

    def current_dataset_process_state(
        self, project_id: str, dataset_id: str
    ) -> Tuple[str, float]:
        """Current processing state of a dataset.

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id

        Returns:
            Tuple[str, float]: semantic name of state of processing, percent done of job
        """
        endpoint_path = (
            self.api_endpoint
            + "/projects/{}/datasets/{}/process_state".format(project_id, dataset_id)
        )

        r = requests_retry.get(endpoint_path, headers=self._get_creds_headers())
        raise_resp_exception_error(r)
        parsed = r.json()
        return parsed["current_state"], parsed["percent_done"]

    def current_abstract_dataset_process_step_status(
        self, project_id: str, dataset_id: str
    ) -> Dict[str, Any]:
        """Returns the process steps statuses for a given dataset or inferenceset

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id

        Returns:
            Dict[str, Any]: A set of process step statuses that exist for a given abstract dataset
        """
        endpoint_path = (
            self.api_endpoint
            + "/projects/{}/datasets/{}/process_step_status".format(
                project_id, dataset_id
            )
        )

        r = requests_retry.get(endpoint_path, headers=self._get_creds_headers())
        raise_resp_exception_error(r)
        parsed: Dict[str, Any] = r.json()
        return parsed

    @staticmethod
    def parse_normalize_process_step_status(
        process_step_status_payload: Dict[str, Any]
    ) -> str:
        result: str = process_step_status_payload["process_step_statuses"]["normalize"][
            "status"
        ]
        return result

    def inferences_exists(
        self, project_id: str, dataset_id: str, inferences_id: str
    ) -> bool:
        """Check if a set of inferences exists.

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id
            inferences_id (str): inferences_id

        Returns:
            bool: Whether the inferences id already exists.
        """
        # TODO: FIXME: We need a first class model for inferences,
        # not just name gluing
        inferences_dataset_id = "_".join(["inferences", dataset_id, inferences_id])
        datasets = self.get_datasets(project_id, include_archived=True)
        existing_dataset_ids = [dataset.get("id") for dataset in datasets]
        return inferences_dataset_id in existing_dataset_ids

    def is_inferences_processed(
        self, project_id: str, dataset_id: str, inferences_id: str
    ) -> bool:
        """Check if a set of inferences is fully processed.

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id
            inferences_id(str): inferences_id

        Returns:
            bool: If the inferences set is done processing.
        """
        endpoint_path = (
            self.api_endpoint
            + "/projects/{}/datasets/{}/inferences/{}/is_processed".format(
                project_id, dataset_id, inferences_id
            )
        )

        r = requests_retry.get(endpoint_path, headers=self._get_creds_headers())
        raise_resp_exception_error(r)
        parsed = r.json()
        processed: bool = parsed["processed"]
        return processed

    def get_inferences_ingest_error_logs(
        self, project_id: str, dataset_id: str, inferences_id: str
    ) -> List[Dict[str, Any]]:
        """Get ingest error log entries for an inference set.

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id
            inferences_id(str): inferences_id

        Returns:
            list[dict]: List of error entries
        """
        endpoint_path = (
            self.api_endpoint
            + "/projects/{}/datasets/{}/inferences/{}/ingest_error_logs".format(
                project_id, dataset_id, inferences_id
            )
        )

        r = requests_retry.get(endpoint_path, headers=self._get_creds_headers())
        raise_resp_exception_error(r)
        parsed: List[Dict[str, Any]] = r.json()
        return parsed

    def current_inferences_process_state(
        self, project_id: str, dataset_id: str, inferences_id: str
    ) -> Tuple[str, float]:
        """current processing state of inferences.

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id
            inferences_id(str): inferences_id

        Returns:
            Tuple[str, float]: semantic name of state of processing, percent done of job
        """
        endpoint_path = (
            self.api_endpoint
            + "/projects/{}/datasets/{}/inferences/{}/process_state".format(
                project_id, dataset_id, inferences_id
            )
        )

        r = requests_retry.get(endpoint_path, headers=self._get_creds_headers())
        raise_resp_exception_error(r)
        parsed = r.json()
        return parsed["current_state"], parsed["percent_done"]

    def upload_asset_from_filepath(
        self, project_id: str, dataset_id: str, filepath: str
    ) -> str:
        """Upload an asset from a local file path.
        This is useful in cases where you have data on your local machine that you want to mirror in aquarium.

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id
            filepath (str): The filepath to grab the assset data from

        Returns:
            str: The URL to the mirrored asset.
        """

        get_upload_path = (
            self.api_endpoint
            + "/projects/{}/datasets/{}/get_upload_url".format(project_id, dataset_id)
        )

        upload_filename = os.path.basename(filepath)
        upload_filename = "{}_{}".format(str(uuid4()), upload_filename)

        params = {"upload_filename": upload_filename}
        upload_url_resp = requests_retry.get(
            get_upload_path, headers=self._get_creds_headers(), params=params
        )

        raise_resp_exception_error(upload_url_resp)
        urls = upload_url_resp.json()
        put_url = urls["put_url"]
        download_url: str = urls["download_url"]

        with open(filepath, "rb") as f:
            upload_resp = requests_retry.put(put_url, data=f)

        raise_resp_exception_error(upload_resp)
        return download_url

    def upload_asset_from_url(
        self, project_id: str, dataset_id: str, source_url: str
    ) -> str:
        """Upload an asset from a private url.
        This is useful in cases where you have data easily accessible on your network that you want to mirror in aquarium.

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id
            source_url (str): The source url to grab the assset data from

        Returns:
            str: The URL to the mirrored asset.
        """
        get_upload_path = (
            self.api_endpoint
            + "/projects/{}/datasets/{}/get_upload_url".format(project_id, dataset_id)
        )

        upload_filename = os.path.basename(source_url)
        upload_filename = "{}_{}".format(str(uuid4()), upload_filename)

        params = {"upload_filename": upload_filename}
        upload_url_resp = requests_retry.get(
            get_upload_path, headers=self._get_creds_headers(), params=params
        )

        raise_resp_exception_error(upload_url_resp)
        urls = upload_url_resp.json()
        put_url = urls["put_url"]
        download_url: str = urls["download_url"]

        dl_resp = requests_retry.get(source_url)
        payload = BytesIO(dl_resp.content)

        upload_resp = requests_retry.put(put_url, data=payload)

        raise_resp_exception_error(upload_resp)
        return download_url

    def _upload_rows_from_files(
        self,
        project_id: str,
        dataset_id: str,
        upload_prefix: str,
        upload_suffix: str,
        file_names: List[str],
        delete_after_upload: bool = True,
    ) -> List[str]:
        # Get upload / download URLs
        get_upload_path = (
            self.api_endpoint
            + "/projects/{}/datasets/{}/get_upload_url".format(project_id, dataset_id)
        )

        download_urls = _upload_local_files(
            file_names,
            get_upload_path,
            self._get_creds_headers(),
            upload_prefix,
            upload_suffix,
            delete_after_upload=delete_after_upload,
        )

        return download_urls

    def update_dataset_frames(
        self,
        project_id: str,
        dataset_id: str,
        update: List[UpdateFrame],
        upload_version: Optional[str] = None,
    ) -> None:
        raise Exception("Not Implemented")

    def update_dataset_labels(
        self,
        project_id: str,
        dataset_id: str,
        update: List[UpdateGTLabelSet],
        upload_version: Optional[str] = None,
    ) -> None:
        raise Exception("Not Implemented")

    def update_inference_labels(
        self,
        project_id: str,
        dataset_id: str,
        update: List[UpdateInferenceLabelSet],
        upload_version: Optional[str] = None,
    ) -> None:
        raise Exception("Not Implemented")

    def _check_first_frame(
        self, first_frame_dict: Dict[str, Any], dataset: LabeledDataset
    ) -> None:
        sensor_data = first_frame_dict.get("sensor_data")
        if sensor_data is None:
            raise Exception("First frame contains zero sensor/media inputs.")

        for sensor in sensor_data:
            urls = list(sensor.get("data_urls").values())
            local_results = check_urls(urls, None)
            r = requests_retry.post(
                self.api_endpoint + "/datasets/verify_urls",
                headers=self._get_creds_headers(),
                json={"urls": urls},
            )
            server_results = r.json()
            mode = get_mode(urls, local_results, server_results)
            errors = get_errors(mode, dataset)

            if len(errors) > 0:
                print(f"WARNING! SOME URL ACCESS ERRORS FOUND!")
                print(f"Errors found: {errors}")
            else:
                print("No errors found when checking first frame!")

    def create_or_update_dataset(
        self,
        project_id: str,
        dataset_id: str,
        data_url: Optional[str] = None,
        embeddings_url: Optional[str] = None,
        dataset: Optional[LabeledDataset] = None,
        wait_until_finish: bool = False,
        wait_timeout: datetime.timedelta = datetime.timedelta(hours=2),
        embedding_distance_metric: str = "euclidean",
        preview_first_frame: bool = False,
        delete_cache_files_after_upload: bool = True,
        check_first_frame: bool = True,
        external_metadata: Optional[Dict[str, Any]] = None,
        pipeline_mode: str = "BATCH",
        is_unlabeled_indexed_dataset: bool = False,
        seed_dataset_name_for_unlabeled_search: Optional[str] = None,
        is_anon_mode: bool = False,
        existing_embedding_version_uuid: Optional[str] = None,
    ) -> None:
        """Create or update a dataset with the provided data urls. Dataset must be created using STREAMING pipeline_mode to update.

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id
            data_url (Optional[str], optional): A URL to the serialized dataset entries.
            embeddings_url (Optional[str], optional): A URL to the serialized dataset embeddings. Defaults to None.
            dataset (Optional[LabeledDataset], optional): The LabeledDataset to upload.
            wait_until_finish (bool, optional): Block until the dataset processing job finishes. This generally takes at least 5 minutes, and scales with the size of the dataset. Defaults to False.
            wait_timeout (datetime.timedelta, optional): Maximum time to wait for. Defaults to 2 hours.
            embedding_distance_metric (str, optional): Distance metric to use for embedding layout. Can be a member of ['euclidean', 'cosine']. Defaults to 'euclidean'.
            preview_first_frame (bool, optional): preview the first frame of the dataset in the webapp before continuing. Requires interaction.
            delete_cache_files_after_upload (bool, optional): flag to turn off automatic deletion of cache files after upload. Useful for ipython notebook users that reload/re-attempt uploads. Defaults to True.
            external_metadata (Optional[Dict[str, Any]], optional): A JSON object that can be used to attach metadata to the dataset itself
            pipeline_mode (str, optional): BATCH or STREAMING
            is_unlabeled_indexed_dataset (bool, optional): Whether this dataset is meant to be used as the seed dataset for unlabeled indexed search.
            seed_dataset_name_for_unlabeled_search (Optional[str], optional): (DEPRECATED). The name of the existing dataset or inf set whose issue elts will be used as the seed for unlabeled indexed search.
            is_anon_mode (bool, optional): flag to tell aquarium if url images are reachable from public internet or shared bucket. False if reachable, True if Not.
            existing_embedding_version_uuid (str, optional): uuid of the embedding version of an existing dataset that shares the same embedding space.
        """

        if is_unlabeled_indexed_dataset:
            if not existing_embedding_version_uuid:
                raise Exception(
                    "'existing_embedding_version_uuid' must be specified if uploading an unlabeled indexed dataset."
                )

        if seed_dataset_name_for_unlabeled_search:
            raise Exception(
                "'seed_dataset_name_for_unlabeled_search' is a deprecated field. See docs on using 'existing_embedding_version_uuid' instead."
            )

        if (
            dataset is not None
            and not is_unlabeled_indexed_dataset
            and dataset.labels_with_confidence
        ):
            raise Exception(
                "Dataset contains GT labels with confidence, this is only valid for unlabeled indexed datasets."
            )

        if pipeline_mode == "STREAMING":
            return self._create_or_update_dataset_streaming(
                project_id,
                dataset_id,
                data_url=data_url,
                embeddings_url=embeddings_url,
                dataset=dataset,
                wait_until_finish=wait_until_finish,
                wait_timeout=wait_timeout,
                embedding_distance_metric=embedding_distance_metric,
                preview_first_frame=preview_first_frame,
                delete_cache_files_after_upload=delete_cache_files_after_upload,
                check_first_frame=check_first_frame,
                external_metadata=external_metadata,
                is_anon_mode=is_anon_mode,
                is_unlabeled_indexed_dataset=is_unlabeled_indexed_dataset,
                existing_embedding_version_uuid=existing_embedding_version_uuid,
            )

        assert_valid_name(dataset_id)

        if embedding_distance_metric not in ["euclidean", "cosine"]:
            raise Exception("embedding_distance_metric must be euclidean or cosine.")

        if not isinstance(wait_timeout, datetime.timedelta):
            raise Exception("wait_timeout must be a datetime.timedelta object")

        if self.dataset_exists(project_id, dataset_id):
            raise Exception("Cannot update dataset when using the BATCH pipeline.")

        if dataset:
            if len(dataset._frame_ids_set) == 0:
                raise Exception("Dataset contains no frames and cannot be empty.")

            dataset._flush_to_disk()

            project_info = self.get_project(project_id)

            dataset._validate_frames(project_info)

            if len(dataset._temp_frame_file_names) == 0:
                raise Exception("Cannot create dataset with 0 frames")

            if preview_first_frame:
                first_frame_dict = dataset.get_first_frame_dict()
                self._preview_frame_dict(
                    project_id,
                    {"labeled_frame": first_frame_dict, "inference_frame": None},
                )
                user_response = input(
                    "Please vist above URL to see your Preview frame.\n\n"
                    "Press ENTER to continue or type `exit` and press ENTER "
                    "to cancel dataset upload.\n"
                )
                if user_response == "exit":
                    print("Canceling dataset upload!")
                    return

            if check_first_frame:
                first_frame_dict = dataset.get_first_frame_dict()
                self._check_first_frame(first_frame_dict, dataset)

            project_info = self.get_project(project_id)
            project_label_set = set(
                [label_class["name"] for label_class in project_info["label_class_map"]]
            )
            extra_dataset_labels = dataset._label_classes_set - project_label_set
            if len(extra_dataset_labels) > 0:
                raise Exception(
                    f"Dataset contains labels {extra_dataset_labels} not in project Label Class Map {project_label_set}. "
                    f"Label Class Maps can be updated using append-only logic as specified here. "
                    f"https://aquarium.gitbook.io/aquarium-changelog/changelog-entries/2021-01-22#updating-label-class-maps"
                )

            print("Uploading Labeled Dataset...")
            upload_prefix = "{}_data".format(str(uuid4()))
            upload_suffix = ".jsonl"
            final_urls = self._upload_rows_from_files(
                project_id,
                dataset_id,
                upload_prefix,
                upload_suffix,
                dataset._temp_frame_file_names,
                delete_after_upload=delete_cache_files_after_upload,
            )
        elif data_url:
            final_urls = [
                data_url,
            ]
        else:
            raise Exception("Please provide either a data_url or dataset argument")

        datasets_api_root = self.api_endpoint + "/projects/{}/datasets".format(
            project_id
        )
        payload = {
            "dataset_id": dataset_id,
            "data_url": final_urls,
            "embedding_distance_metric": embedding_distance_metric,
            "embedding_upload_version": 1,
            "is_anon_mode": is_anon_mode,
            "existing_embedding_version_uuid": existing_embedding_version_uuid,
        }

        if is_unlabeled_indexed_dataset:
            payload["is_unlabeled_indexed_dataset"] = True

        if external_metadata is not None:
            if not isinstance(external_metadata, dict) or (
                external_metadata and not isinstance(next(iter(external_metadata)), str)
            ):
                raise Exception("external_metadata must be a dict with string keys")
            payload["external_metadata"] = external_metadata

        if dataset and dataset._temp_frame_embeddings_file_names:
            print("Uploading Labeled Dataset Embeddings...")
            upload_prefix = "{}_embeddings".format(str(uuid4()))
            upload_suffix = ".arrow"
            uploaded_urls = self._upload_rows_from_files(
                project_id,
                dataset_id,
                upload_prefix,
                upload_suffix,
                dataset._temp_frame_embeddings_file_names,
                delete_after_upload=delete_cache_files_after_upload,
            )
            if uploaded_urls:  # not empty list
                payload["embeddings_url"] = uploaded_urls
        elif embeddings_url:
            payload["embeddings_url"] = [
                embeddings_url,
            ]

        if dataset and dataset._temp_frame_asset_file_names:
            print("Uploading Labeled Frame Assets...")
            upload_prefix = "{}_assets".format(str(uuid4()))
            upload_suffix = ".arrow"
            uploaded_urls = self._upload_rows_from_files(
                project_id,
                dataset_id,
                upload_prefix,
                upload_suffix,
                dataset._temp_frame_asset_file_names,
                delete_after_upload=delete_cache_files_after_upload,
            )
            if uploaded_urls:  # not empty list
                payload["frame_asset_url"] = uploaded_urls

        # TODO: Should we just make it not optional, because very few (if any?)
        # people are still using the old data url flow
        if dataset is not None:
            dataset._cleanup_temp_dir()

        print("Dataset Processing Initiating...")
        r = requests_retry.post(
            datasets_api_root, headers=self._get_creds_headers(), json=payload
        )
        raise_resp_exception_error(r)
        print("Dataset Processing Initiated Successfully")

        if wait_until_finish:
            print(f"Dataset Processing is waiting on workers to spin up...")
            normalize_status = "PENDING"
            while normalize_status == "PENDING":
                time.sleep(10)
                normalize_status = Client.parse_normalize_process_step_status(
                    self.current_abstract_dataset_process_step_status(
                        project_id, dataset_id
                    )
                )
                full_process_state, _ = self.current_dataset_process_state(
                    project_id, dataset_id
                )
                if full_process_state == "FAILED":
                    print("Dataset processing has failed. Exiting...")
                    return
            print(f"Dataset Processing Workers have been spun up.")
            with tqdm(
                total=100.0,
                file=sys.stdout,
                unit_scale=True,
                desc="Dataset Processing Progress",
            ) as pbar:  # type: tqdm[Any]
                start_time = datetime.datetime.now()
                processing_state = "PENDING"

                display_processing_state: Callable[
                    [str], str
                ] = lambda state: f"Dataset Processing Status: {state}"
                pbar.write(display_processing_state(processing_state))
                while (datetime.datetime.now() - start_time) < wait_timeout:
                    (
                        new_processing_state,
                        new_percent_done,
                    ) = self.current_dataset_process_state(project_id, dataset_id)
                    pbar.update(new_percent_done - pbar.n)
                    if new_processing_state != processing_state:
                        processing_state = new_processing_state
                        pbar.write(display_processing_state(processing_state))
                    processed = self.is_dataset_processed(
                        project_id=project_id, dataset_id=dataset_id
                    )
                    if processed:
                        pbar.update(100.0 - pbar.n)
                        pbar.close()
                        print("Dataset is fully processed.")
                        break
                    if processing_state == "FAILED":
                        pbar.update(100.0 - pbar.n)
                        pbar.close()
                        print("Dataset processing has failed. Exiting...")
                        raw_logs = self.get_dataset_ingest_error_logs(
                            project_id, dataset_id
                        )
                        formatted = self._format_error_logs(raw_logs)
                        for entry in formatted:
                            print(entry)

                        break
                    else:
                        time.sleep(10)

                if datetime.datetime.now() - start_time >= wait_timeout:
                    pbar.close()
                    print("Exceeded timeout waiting for job completion.")

    def create_dataset(
        self,
        project_id: str,
        dataset_id: str,
        data_url: Optional[str] = None,
        embeddings_url: Optional[str] = None,
        dataset: Optional[LabeledDataset] = None,
        wait_until_finish: bool = False,
        wait_timeout: datetime.timedelta = datetime.timedelta(hours=2),
        embedding_distance_metric: str = "euclidean",
        preview_first_frame: bool = False,
        delete_cache_files_after_upload: bool = True,
        check_first_frame: bool = True,
        external_metadata: Optional[Dict[str, Any]] = None,
        pipeline_mode: str = "BATCH",
        is_unlabeled_indexed_dataset: bool = False,
        seed_dataset_name_for_unlabeled_search: Optional[str] = None,
        is_anon_mode: bool = False,
        existing_embedding_version_uuid: Optional[str] = None,
    ) -> None:
        """Create or update a dataset with the provided data urls. Dataset must be created using STREAMING pipeline_mode to update. (backcompat shortcut for create_or_update_dataset(...))

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id
            data_url (Optional[str], optional): A URL to the serialized dataset entries.
            embeddings_url (Optional[str], optional): A URL to the serialized dataset embeddings. Defaults to None.
            dataset (Optional[LabeledDataset], optional): The LabeledDataset to upload.
            wait_until_finish (bool, optional): Block until the dataset processing job finishes. This generally takes at least 5 minutes, and scales with the size of the dataset. Defaults to False.
            wait_timeout (datetime.timedelta, optional): Maximum time to wait for. Defaults to 2 hours.
            embedding_distance_metric (str, optional): Distance metric to use for embedding layout. Can be a member of ['euclidean', 'cosine']. Defaults to 'euclidean'.
            preview_first_frame (bool, optional): preview the first frame of the dataset in the webapp before continuing. Requires interaction.
            delete_cache_files_after_upload (bool, optional): flag to turn off automatic deletion of cache files after upload. Useful for ipython notebook users that reload/re-attempt uploads. Defaults to True.
            external_metadata (Optional[Dict[str, Any]], optional): A JSON object that can be used to attach metadata to the dataset itself
            pipeline_mode (str, optional): BATCH or STREAMING
            is_unlabeled_indexed_dataset (bool, optional): Whether this dataset is meant to be used as the seed dataset for unlabeled indexed search.
            seed_dataset_name_for_unlabeled_search (Optional[str], optional): (DEPRECATED). The name of the existing dataset or inf set whose issue elts will be used as the seed for unlabeled indexed search.
            is_anon_mode (bool, optional): flag to tell aquarium if url images are reachable from public internet or shared bucket. False if reachable, True if Not.
            existing_embedding_version_uuid (str, optional): uuid of the embedding version of an existing dataset that shares the same embedding space.
        """

        return self.create_or_update_dataset(
            project_id,
            dataset_id,
            data_url=data_url,
            embeddings_url=embeddings_url,
            dataset=dataset,
            wait_until_finish=wait_until_finish,
            wait_timeout=wait_timeout,
            embedding_distance_metric=embedding_distance_metric,
            preview_first_frame=preview_first_frame,
            delete_cache_files_after_upload=delete_cache_files_after_upload,
            check_first_frame=check_first_frame,
            external_metadata=external_metadata,
            pipeline_mode=pipeline_mode,
            is_unlabeled_indexed_dataset=is_unlabeled_indexed_dataset,
            seed_dataset_name_for_unlabeled_search=seed_dataset_name_for_unlabeled_search,
            is_anon_mode=is_anon_mode,
            existing_embedding_version_uuid=existing_embedding_version_uuid,
        )

    def _create_or_update_dataset_streaming(
        self,
        project_id: str,
        dataset_id: str,
        data_url: Optional[str] = None,
        embeddings_url: Optional[str] = None,
        dataset: Optional[LabeledDataset] = None,
        wait_until_finish: bool = False,
        wait_timeout: datetime.timedelta = datetime.timedelta(hours=2),
        embedding_distance_metric: str = "euclidean",
        preview_first_frame: bool = False,
        delete_cache_files_after_upload: bool = True,
        check_first_frame: bool = True,
        external_metadata: Optional[Dict[str, Any]] = None,
        is_anon_mode: bool = False,
        is_unlabeled_indexed_dataset: bool = False,
        upload_version: Optional[str] = None,
        existing_embedding_version_uuid: Optional[str] = None,
    ) -> None:
        """INTERNAL: Create or update a streaming dataset with the provided data urls. The dataset will be processed by the streaming pipeline and will support updates.

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id
            data_url (Optional[str], optional): A URL to the serialized dataset entries.
            embeddings_url (Optional[str], optional): A URL to the serialized dataset embeddings. Defaults to None.
            dataset (Optional[LabeledDataset], optional): The LabeledDataset to upload.
            wait_until_finish (bool, optional): Block until the dataset processing job finishes. This generally takes at least 5 minutes, and scales with the size of the dataset. Defaults to False.
            wait_timeout (datetime.timedelta, optional): Maximum time to wait for. Defaults to 2 hours.
            embedding_distance_metric (str, optional): Distance metric to use for embedding layout. Can be a member of ['euclidean', 'cosine']. Defaults to 'euclidean'.
            preview_first_frame (bool, optional): preview the first frame of the dataset in the webapp before continuing. Requires interaction.
            delete_cache_files_after_upload (bool, optional): flag to turn off automatic deletion of cache files after upload. Useful for ipython notebook users that reload/re-attempt uploads. Defaults to True.
            external_metadata (Optional[Dict[str, Any]], optional): A JSON object that can be used to attach metadata to the dataset itself
            is_anon_mode (bool, optional): flag to tell aquarium if url images are reachable from public internet or shared bucket. False if reachable, True if Not.
            upload_version (str, optional): A name for a distinct set of frames that are new or updated within the dataset, for comparison down the line. Autogenerated for new datasets or if `wait_until_finish` is True, then defaults to last-created upload version.
        """

        assert_valid_name(dataset_id)

        if wait_until_finish and not upload_version:
            upload_version = str(uuid4())

        if embedding_distance_metric not in ["euclidean", "cosine"]:
            raise Exception("embedding_distance_metric must be euclidean or cosine.")

        if not isinstance(wait_timeout, datetime.timedelta):
            raise Exception("wait_timeout must be a datetime.timedelta object")

        if not dataset:
            raise Exception("Please provide either a data_url or dataset argument")

        if self.is_dataset_archived(project_id, dataset_id):
            raise Exception("Cannot upload streaming frames to archived dataset")

        if len(dataset._frame_ids_set) == 0:
            raise Exception("Dataset contains no frames and cannot be empty.")

        dataset._flush_to_disk()

        if dataset and dataset._temp_frame_asset_file_names:
            raise Exception(
                "Mutable streaming datasets do not support mask_data for semseg masks yet."
            )

        project_info = self.get_project(project_id)

        dataset._validate_frames(project_info)

        if len(dataset._temp_frame_file_names_streaming) == 0:
            raise Exception("Cannot create dataset with 0 frames")

        if preview_first_frame:
            first_frame_dict = dataset.get_first_frame_dict()
            self._preview_frame_dict(
                project_id,
                {"labeled_frame": first_frame_dict, "inference_frame": None},
            )
            user_response = input(
                "Please vist above URL to see your Preview frame.\n\n"
                "Press ENTER to continue or type `exit` and press ENTER "
                "to cancel dataset upload.\n"
            )
            if user_response == "exit":
                print("Canceling dataset upload!")
                return

        if check_first_frame:
            first_frame_dict = dataset.get_first_frame_dict()
            self._check_first_frame(first_frame_dict, dataset)

        project_info = self.get_project(project_id)
        project_label_set = set(
            [label_class["name"] for label_class in project_info["label_class_map"]]
        )
        extra_dataset_labels = dataset._label_classes_set - project_label_set
        if len(extra_dataset_labels) > 0:
            raise Exception(
                f"Dataset contains labels {extra_dataset_labels} not in project Label Class Map {project_label_set}. "
                f"Label Class Maps can be updated using append-only logic as specified here. "
                f"https://aquarium.gitbook.io/aquarium-changelog/changelog-entries/2021-01-22#updating-label-class-maps"
            )

        print("Uploading Labeled Dataset...")
        uuid_prefix = str(uuid4())
        upload_prefix_frame = "{}_frame_data".format(uuid_prefix)
        upload_prefix_crop = "{}_crop_data".format(uuid_prefix)
        upload_suffix = ".jsonl"

        frame_urls = self._upload_rows_from_files(
            project_id,
            dataset_id,
            upload_prefix_frame,
            upload_suffix,
            dataset._temp_frame_file_names_streaming,
            delete_after_upload=delete_cache_files_after_upload,
        )
        crop_urls = self._upload_rows_from_files(
            project_id,
            dataset_id,
            upload_prefix_crop,
            upload_suffix,
            dataset._temp_crop_file_names_streaming,
            delete_after_upload=delete_cache_files_after_upload,
        )
        final_urls = {
            "frame": frame_urls,
            "crop": crop_urls,
        }

        if dataset and dataset._temp_frame_embeddings_file_names_streaming:
            print("Uploading Labeled Dataset Embeddings...")
            upload_frame_prefix = "{}_frame_embeddings".format(str(uuid4()))
            upload_crop_prefix = "{}_crop_embeddings".format(str(uuid4()))
            upload_suffix = ".arrow"
            uploaded_frame_urls = self._upload_rows_from_files(
                project_id,
                dataset_id,
                upload_frame_prefix,
                upload_suffix,
                dataset._temp_frame_embeddings_file_names_streaming,
                delete_after_upload=delete_cache_files_after_upload,
            )
            uploaded_crop_urls = self._upload_rows_from_files(
                project_id,
                dataset_id,
                upload_crop_prefix,
                upload_suffix,
                dataset._temp_crop_embeddings_file_names_streaming,
                delete_after_upload=delete_cache_files_after_upload,
            )
            if uploaded_frame_urls:  # not empty list
                final_urls["frame_embeddings"] = uploaded_frame_urls
            if uploaded_crop_urls:  # not empty list
                final_urls["crop_embeddings"] = uploaded_crop_urls

        if dataset and dataset._temp_frame_asset_file_names:
            print("Uploading Labeled Frame Assets...")
            upload_prefix = "{}_assets".format(str(uuid4()))
            upload_suffix = ".arrow"
            uploaded_urls = self._upload_rows_from_files(
                project_id,
                dataset_id,
                upload_prefix,
                upload_suffix,
                dataset._temp_frame_asset_file_names,
                delete_after_upload=delete_cache_files_after_upload,
            )
            if uploaded_urls:  # not empty list
                final_urls["frame_asset_url"] = uploaded_urls

        datasets_api_root = self.api_endpoint + "/projects/{}/datasets".format(
            project_id
        )
        payload = {
            "dataset_id": dataset_id,
            "data_url": final_urls,
            "embedding_distance_metric": embedding_distance_metric,
            "embedding_upload_version": 1,
            "upload_version": upload_version,
            "pipeline_mode": "STREAMING",
            "is_anon_mode": is_anon_mode,
            "is_unlabeled_indexed_dataset": is_unlabeled_indexed_dataset,
            "existing_embedding_version_uuid": existing_embedding_version_uuid,
            "frame_embedding_dim": dataset.frame_embedding_dim,
            "crop_embedding_dim": dataset.crop_embedding_dim,
            "sample_frame_embeddings": dataset.sample_frame_embeddings,
            "sample_crop_embeddings": dataset.sample_crop_embeddings,
        }

        if external_metadata is not None:
            if not isinstance(external_metadata, dict) or (
                external_metadata and not isinstance(next(iter(external_metadata)), str)
            ):
                raise Exception("external_metadata must be a dict with string keys")
            payload["external_metadata"] = external_metadata

        # TODO: Should we just make it not optional, because very few (if any?)
        # people are still using the old data url flow
        if dataset is not None:
            dataset._cleanup_temp_dir()

        print("Dataset Processing Initiating...")
        r = requests_retry.post(
            datasets_api_root, headers=self._get_creds_headers(), json=payload
        )
        raise_resp_exception_error(r)
        print("Dataset Processing Initiated Successfully")

        if wait_until_finish:
            # Wait for windows to finish on the dataset
            print("Waiting for dataset to finish processing...")
            all_upload_version_windows_done = False
            start_time = datetime.datetime.now()
            dataset_upload_version_windows = []
            while not all_upload_version_windows_done:
                r = requests_retry.get(
                    self.api_endpoint
                    + "/streaming/projects/{}/datasets/{}/upload_version/{}/windows".format(
                        project_id,
                        dataset_id,
                        upload_version,
                    ),
                    headers=self._get_creds_headers(),
                )
                if r.ok:
                    dataset_upload_version_windows = r.json()
                    all_upload_version_windows_done = len(
                        dataset_upload_version_windows
                    ) > 0 and all(
                        window.get("status") == "DONE"
                        or window.get("status") == "WINDOW_ERRORED"
                        or window.get("status") == "AGG_ERRORED"
                        for window in dataset_upload_version_windows
                    )
                if datetime.datetime.now() - start_time >= wait_timeout:
                    print("Exceeded timeout waiting for dataset to finish processing.")
                    return
                time.sleep(10)
            errored_window_uuids = [
                window.get("uuid")
                for window in dataset_upload_version_windows
                if (
                    (window.get("status") == "WINDOW_ERRORED")
                    or (window.get("status") == "AGG_ERRORED")
                )
            ]
            if len(errored_window_uuids) > 0:
                print(
                    "Dataset processing has {}failed.".format(
                        "partially "
                        if len(errored_window_uuids)
                        < len(dataset_upload_version_windows)
                        else ""
                    )
                )
                print(
                    "Check project uploads to see more details and which frames need reuploading."
                )
                print(
                    "Failed Upload IDs: {}".format(
                        ", ".join(str(x) for x in errored_window_uuids)
                    )
                )
                print(
                    "{}/projects/{}/details?tab=streaming_uploads".format(
                        self.api_endpoint[:-7], project_id
                    )
                )
            else:
                print("Dataset is fully processed.")

    def add_to_streaming_dataset(
        self,
        project_id: str,
        dataset_id: str,
        dataset: Optional[LabeledDataset] = None,
        embedding_distance_metric: str = "euclidean",
        delete_cache_files_after_upload: bool = True,
        external_metadata: Optional[Dict[str, Any]] = None,
        is_anon_mode: bool = False,
        upload_version: str = None,
        validate_frames: bool = False,
        reuse_embeddings: bool = False,
    ) -> None:
        """Append or update a streaming dataset with the provided data urls. Dataset must be have already been created using STREAMING pipeline_mode.

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id
            dataset (Optional[LabeledDataset], optional): The LabeledDataset to upload.
            embedding_distance_metric (str, optional): Distance metric to use for embedding layout. Can be a member of ['euclidean', 'cosine']. Defaults to 'euclidean'.
            delete_cache_files_after_upload (bool, optional): flag to turn off automatic deletion of cache files after upload. Useful for ipython notebook users that reload/re-attempt uploads. Defaults to True.
            external_metadata (Optional[Dict[str, Any]], optional): A JSON object that can be used to attach metadata to the dataset itself
            is_anon_mode (bool, optional): flag to tell aquarium if url images are reachable from public internet or shared bucket. False if reachable, True if Not.
            upload_version (str, optional): A name for a distinct set of frames that are new or updated within the dataset, for comparison down the line. Defaults to last-created upload version.
            validate_frames (bool, optional): Flag to tell the client to pre-check that all queued frames conform to a project's primary_task params. Defaults to False
        """

        assert_valid_name(dataset_id)

        if embedding_distance_metric not in ["euclidean", "cosine"]:
            raise Exception("embedding_distance_metric must be euclidean or cosine.")

        if not dataset:
            raise Exception("Please provide either a data_url or dataset argument")

        dataset._flush_to_disk()

        if dataset and dataset._temp_frame_asset_file_names:
            raise Exception(
                "Mutable streaming datasets do not support mask_data for semseg masks yet."
            )

        if validate_frames:
            project_info = self.get_project(project_id)
            dataset._validate_frames(project_info)

            project_label_set = set(
                [label_class["name"] for label_class in project_info["label_class_map"]]
            )
            extra_dataset_labels = dataset._label_classes_set - project_label_set
            if len(extra_dataset_labels) > 0:
                raise Exception(
                    f"Dataset contains labels {extra_dataset_labels} not in project Label Class Map {project_label_set}. "
                    f"Label Class Maps can be updated using append-only logic as specified here. "
                    f"https://aquarium.gitbook.io/aquarium-changelog/changelog-entries/2021-01-22#updating-label-class-maps"
                )

        if len(dataset._temp_frame_file_names_streaming) == 0:
            raise Exception("Cannot append 0 frames to a dataset")

        print("Adding to Labeled Dataset...")
        uuid_prefix = str(uuid4())
        upload_prefix_frame = "{}_frame_data".format(uuid_prefix)
        upload_prefix_crop = "{}_crop_data".format(uuid_prefix)
        upload_suffix = ".jsonl"

        frame_urls = self._upload_rows_from_files(
            project_id,
            dataset_id,
            upload_prefix_frame,
            upload_suffix,
            dataset._temp_frame_file_names_streaming,
            delete_after_upload=delete_cache_files_after_upload,
        )
        crop_urls = self._upload_rows_from_files(
            project_id,
            dataset_id,
            upload_prefix_crop,
            upload_suffix,
            dataset._temp_crop_file_names_streaming,
            delete_after_upload=delete_cache_files_after_upload,
        )
        final_urls = {
            "frame": frame_urls,
            "crop": crop_urls,
        }

        if dataset and dataset._temp_frame_embeddings_file_names_streaming:
            print("Uploading Labeled Dataset Embeddings...")
            upload_frame_prefix = "{}_frame_embeddings".format(str(uuid4()))
            upload_crop_prefix = "{}_crop_embeddings".format(str(uuid4()))
            upload_suffix = ".arrow"
            uploaded_frame_urls = self._upload_rows_from_files(
                project_id,
                dataset_id,
                upload_frame_prefix,
                upload_suffix,
                dataset._temp_frame_embeddings_file_names_streaming,
                delete_after_upload=delete_cache_files_after_upload,
            )
            uploaded_crop_urls = self._upload_rows_from_files(
                project_id,
                dataset_id,
                upload_crop_prefix,
                upload_suffix,
                dataset._temp_crop_embeddings_file_names_streaming,
                delete_after_upload=delete_cache_files_after_upload,
            )
            if uploaded_frame_urls:  # not empty list
                final_urls["frame_embeddings"] = uploaded_frame_urls
            if uploaded_crop_urls:  # not empty list
                final_urls["crop_embeddings"] = uploaded_crop_urls

        if dataset and dataset._temp_frame_asset_file_names:
            print("Uploading Labeled Frame Assets...")
            upload_prefix = "{}_assets".format(str(uuid4()))
            upload_suffix = ".arrow"
            uploaded_urls = self._upload_rows_from_files(
                project_id,
                dataset_id,
                upload_prefix,
                upload_suffix,
                dataset._temp_frame_asset_file_names,
                delete_after_upload=delete_cache_files_after_upload,
            )
            if uploaded_urls:  # not empty list
                final_urls["frame_asset_url"] = uploaded_urls

        datasets_api_root = self.api_endpoint + "/projects/{}/datasets".format(
            project_id
        )
        payload = {
            "dataset_id": dataset_id,
            "data_url": final_urls,
            "embedding_distance_metric": embedding_distance_metric,
            "embedding_upload_version": 1,
            "upload_version": upload_version,
            "pipeline_mode": "STREAMING",
            "is_anon_mode": is_anon_mode,
            "reuse_embeddings": reuse_embeddings,
            "frame_embedding_dim": dataset.frame_embedding_dim,
            "crop_embedding_dim": dataset.crop_embedding_dim,
            "sample_frame_embeddings": dataset.sample_frame_embeddings,
            "sample_crop_embeddings": dataset.sample_crop_embeddings,
        }

        if external_metadata is not None:
            if not isinstance(external_metadata, dict) or (
                external_metadata and not isinstance(next(iter(external_metadata)), str)
            ):
                raise Exception("external_metadata must be a dict with string keys")
            payload["external_metadata"] = external_metadata

        # TODO: Should we just make it not optional, because very few (if any?)
        # people are still using the old data url flow
        if dataset is not None:
            dataset._cleanup_temp_dir()

        print("Dataset Processing Initiating...")
        r = requests_retry.post(
            datasets_api_root, headers=self._get_creds_headers(), json=payload
        )
        raise_resp_exception_error(r)
        print("Dataset Processing Initiated Successfully")

    def update_dataset_metadata(
        self, project_id: str, dataset_id: str, external_metadata: Dict[str, Any]
    ) -> None:
        """Update dataset metadata

        Args:
            project_id (str): The project id.
            dataset_id (str): The dataset id.
            external_metadata (Dict[Any, Any]): The new metadata
        """
        if not isinstance(external_metadata, dict) or (
            external_metadata and not isinstance(next(iter(external_metadata)), str)
        ):
            raise Exception("external_metadata must be a dict with string keys")

        payload = {"external_metadata": external_metadata}
        r = requests_retry.post(
            f"{self.api_endpoint}/projects/{project_id}/datasets/{dataset_id}/metadata",
            headers=self._get_creds_headers(),
            json=payload,
        )
        raise_resp_exception_error(r)

    def create_or_update_inferences(
        self,
        project_id: str,
        dataset_id: str,
        inferences_id: str,
        data_url: Optional[str] = None,
        embeddings_url: Optional[str] = None,
        inferences: Optional[Inferences] = None,
        wait_until_finish: bool = False,
        wait_timeout: datetime.timedelta = datetime.timedelta(hours=2),
        embedding_distance_metric: str = "euclidean",
        delete_cache_files_after_upload: bool = True,
        external_metadata: Optional[Dict[str, Any]] = None,
        pipeline_mode: str = "BATCH",
    ) -> None:
        """Create or update an inference set with the provided data urls. Dataset + Inferences must be created using STREAMING pipeline_mode to update.

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id
            inferences_id (str): A unique identifier for this set of inferences.
            data_url (Optional[str], optional): A URL to the serialized inference entries.
            embeddings_url (Optional[str], optional): A URL to the serialized inference embeddings. Defaults to None.
            inferences (Optional[Inferences], optional): The inferences to upload.
            wait_until_finish (bool, optional): Block until the dataset processing job finishes. This generally takes at least 5 minutes, and scales with the size of the dataset. Defaults to False.
            wait_timeout (datetime.timedelta, optional): Maximum time to wait for. Defaults to 2 hours.
            embedding_distance_metric (str, optional): Distance metric to use for embedding layout. Can be a member of ['euclidean', 'cosine']. Defaults to 'euclidean'.
            delete_cache_files_after_upload (bool, optional): flag to turn off automatic deletion of cache files after upload. Useful for ipython notebook users that reload/re-attempt uploads. Defaults to True.
            external_metadata (Optional[Dict[str, Any]], optional): A JSON object that can be used to attach metadata to the inferences itself
            pipeline_mode (str, optional): BATCH or STREAMING
        """

        assert_valid_name(dataset_id)
        assert_valid_name(inferences_id)
        queue_after_dataset = True

        upload_version = str(uuid4())

        if embedding_distance_metric not in ["euclidean", "cosine"]:
            raise Exception("embedding_distance_metric must be euclidean or cosine.")

        if not isinstance(wait_timeout, datetime.timedelta):
            raise Exception("wait_timeout must be a datetime.timedelta object")

        if not self.dataset_exists(project_id, dataset_id):
            raise Exception(f"Dataset {dataset_id} does not exist")
        if (
            not self.is_dataset_processed(project_id, dataset_id)
            and not queue_after_dataset
        ):
            raise Exception(f"Dataset {dataset_id} is not fully processed")
        # If the dataset is already processed, ignore the queue arg
        if self.is_dataset_processed(project_id, dataset_id) and queue_after_dataset:
            queue_after_dataset = False

        if pipeline_mode == "BATCH" and self.inferences_exists(
            project_id, dataset_id, inferences_id
        ):
            raise Exception("Cannot update inferences when using the BATCH pipeline.")

        inferences_api_root = (
            self.api_endpoint
            + "/projects/{}/datasets/{}/inferences".format(project_id, dataset_id)
        )

        if inferences:
            if len(inferences._frame_ids_set) == 0:
                raise Exception("Inferences contains no frames and cannot be empty.")

            inferences._flush_to_disk()

            if pipeline_mode == "STREAMING" and inferences._temp_frame_asset_file_names:
                raise Exception(
                    "Mutable streaming inferences do not support mask_data for semseg masks yet."
                )

            project_info = self.get_project(project_id)
            project_label_set = set(
                [label_class["name"] for label_class in project_info["label_class_map"]]
            )
            extra_inferences_labels = inferences._label_classes_set - project_label_set
            if len(extra_inferences_labels) > 0:
                raise Exception(
                    f"Dataset contains labels {extra_inferences_labels} not in project Label Class Map {project_label_set}"
                )

            inferences._validate_frames(project_info)
            print("Uploading Inferences...")

            upload_prefix = "{}_data".format(str(uuid4()))
            upload_suffix = ".jsonl"
            final_urls = self._upload_rows_from_files(
                project_id,
                dataset_id,
                upload_prefix,
                upload_suffix,
                inferences._temp_frame_file_names,
                delete_after_upload=delete_cache_files_after_upload,
            )
        elif data_url:
            final_urls = [
                data_url,
            ]
        else:
            raise Exception("Please provide either a data_url or dataset argument")

        payload = {
            "inferences_id": inferences_id,
            "data_url": final_urls,
            "embedding_distance_metric": embedding_distance_metric,
            "embedding_upload_version": 1,
            "queue_after_dataset": queue_after_dataset,
            "upload_version": upload_version,
            "pipeline_mode": pipeline_mode,
            "frame_embedding_dim": inferences.frame_embedding_dim
            if inferences
            else None,
            "crop_embedding_dim": inferences.crop_embedding_dim if inferences else None,
        }

        if external_metadata is not None:
            if not isinstance(external_metadata, dict) or (
                external_metadata and not isinstance(next(iter(external_metadata)), str)
            ):
                raise Exception("external_metadata must be a dict with string keys")
            payload["external_metadata"] = external_metadata

        if inferences and inferences._temp_frame_embeddings_file_names:
            print("Uploading Inference Embeddings...")
            upload_prefix = "{}_embeddings".format(str(uuid4()))
            upload_suffix = ".arrow"
            uploaded_urls = self._upload_rows_from_files(
                project_id,
                dataset_id,
                upload_prefix,
                upload_suffix,
                inferences._temp_frame_embeddings_file_names,
                delete_after_upload=delete_cache_files_after_upload,
            )
            if uploaded_urls:  # not empty list
                payload["embeddings_url"] = uploaded_urls

        if inferences and inferences._temp_frame_asset_file_names:
            print("Uploading Inference Assets...")
            upload_prefix = "{}_assets".format(str(uuid4()))
            upload_suffix = ".arrow"
            uploaded_urls = self._upload_rows_from_files(
                project_id,
                dataset_id,
                upload_prefix,
                upload_suffix,
                inferences._temp_frame_asset_file_names,
                delete_after_upload=delete_cache_files_after_upload,
            )
            if uploaded_urls:  # not empty list
                payload["frame_asset_url"] = uploaded_urls

        elif embeddings_url:
            payload["embeddings_url"] = [
                embeddings_url,
            ]

        # TODO: Should we just make it not optional, because very few (if any?)
        # people are still using the old data url flow
        if inferences is not None:
            inferences._cleanup_temp_dir()

        total_inferences_id = f"inferences_{dataset_id}_{inferences_id}"

        print(f"Inferences Processing Queuing...")

        r = requests_retry.post(
            inferences_api_root, headers=self._get_creds_headers(), json=payload
        )
        raise_resp_exception_error(r)
        print(f"Inferences Processing Queued Successfully")

        if wait_until_finish and pipeline_mode == "STREAMING":
            # Wait for windows to finish on the inference set
            print(f"Waiting for inferences to finish processing...")
            all_upload_version_windows_done = False
            start_time = datetime.datetime.now()
            infset_upload_version_windows = []
            while not all_upload_version_windows_done:
                r = requests_retry.get(
                    self.api_endpoint
                    + "/streaming/projects/{}/datasets/{}/upload_version/{}/windows".format(
                        project_id,
                        total_inferences_id,
                        upload_version,
                    ),
                    headers=self._get_creds_headers(),
                )
                if r.ok:
                    infset_upload_version_windows = r.json()
                    all_upload_version_windows_done = len(
                        infset_upload_version_windows
                    ) > 0 and all(
                        window.get("status") == "DONE"
                        or window.get("status") == "WINDOW_ERRORED"
                        or window.get("status") == "AGG_ERRORED"
                        for window in infset_upload_version_windows
                    )
                if datetime.datetime.now() - start_time >= wait_timeout:
                    print(
                        "Exceeded timeout waiting for inferences to finish processing."
                    )
                    return
                time.sleep(10)
            errored_window_uuids = [
                window.get("uuid")
                for window in infset_upload_version_windows
                if (
                    (window.get("status") == "WINDOW_ERRORED")
                    or (window.get("status") == "AGG_ERRORED")
                )
            ]
            if len(errored_window_uuids) > 0:
                print(
                    "Inferences processing has {}failed.".format(
                        "partially "
                        if len(errored_window_uuids)
                        < len(infset_upload_version_windows)
                        else ""
                    )
                )
                print(
                    "Check project uploads to see more details and which inferences need reuploading."
                )
                print(
                    "Failed Upload IDs: {}".format(
                        ", ".join(str(x) for x in errored_window_uuids)
                    )
                )
                print(
                    "{}/projects/{}/details?tab=streaming_uploads".format(
                        self.api_endpoint[:-7], project_id
                    )
                )
            else:
                print("Inferences are fully processed.")
        elif wait_until_finish and pipeline_mode == "BATCH":
            print(f"Inferences Processing is waiting on workers to spin up...")
            normalize_status = "PENDING"
            while normalize_status == "PENDING":
                time.sleep(10)
                normalize_status = Client.parse_normalize_process_step_status(
                    self.current_abstract_dataset_process_step_status(
                        project_id, total_inferences_id
                    )
                )
                full_process_state, _ = self.current_inferences_process_state(
                    project_id, dataset_id, inferences_id
                )
                if full_process_state == "FAILED":
                    print("Inferences processing has failed. Exiting...")
                    return
            print(f"Inferences Processing Workers have been spun up.")
            with tqdm(
                total=100.0,
                file=sys.stdout,
                unit_scale=True,
                desc="Inferences Processing Progress",
            ) as pbar:  # type: tqdm[Any]
                start_time = datetime.datetime.now()
                processing_state = "PENDING"
                display_processing_state: Callable[
                    [str], str
                ] = lambda state: f"Inferences Processing State: {state}"
                pbar.write(display_processing_state(processing_state))
                while (datetime.datetime.now() - start_time) < wait_timeout:
                    (
                        new_processing_state,
                        new_percent_done,
                    ) = self.current_inferences_process_state(
                        project_id, dataset_id, inferences_id
                    )
                    pbar.update(new_percent_done - pbar.n)
                    if new_processing_state != processing_state:
                        processing_state = new_processing_state
                        pbar.write(display_processing_state(processing_state))
                    processed = self.is_inferences_processed(
                        project_id=project_id,
                        dataset_id=dataset_id,
                        inferences_id=inferences_id,
                    )
                    if processed:
                        pbar.update(100.0 - pbar.n)
                        pbar.close()
                        print("Inferences are fully processed.")
                        break
                    if processing_state == "FAILED":
                        pbar.update(100.0 - pbar.n)
                        pbar.close()
                        print("Inferences processing has failed. Exiting...")
                        raw_logs = self.get_inferences_ingest_error_logs(
                            project_id, dataset_id, inferences_id
                        )
                        formatted = self._format_error_logs(raw_logs)
                        for entry in formatted:
                            print(entry)

                        break
                    else:
                        time.sleep(10)

                if datetime.datetime.now() - start_time >= wait_timeout:
                    pbar.close()
                    print("Exceeded timeout waiting for job completion.")

    def create_inferences(
        self,
        project_id: str,
        dataset_id: str,
        inferences_id: str,
        data_url: Optional[str] = None,
        embeddings_url: Optional[str] = None,
        inferences: Optional[Inferences] = None,
        wait_until_finish: bool = False,
        wait_timeout: datetime.timedelta = datetime.timedelta(hours=2),
        embedding_distance_metric: str = "euclidean",
        delete_cache_files_after_upload: bool = True,
        external_metadata: Optional[Dict[str, Any]] = None,
        pipeline_mode: str = "BATCH",
    ) -> None:
        """Create or update an inference set with the provided data urls. Dataset + Inferences must be created using STREAMING pipeline_mode to update. (backcompat shortcut for create_or_update_inferences(...))

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id
            inferences_id (str): A unique identifier for this set of inferences.
            data_url (Optional[str], optional): A URL to the serialized inference entries.
            embeddings_url (Optional[str], optional): A URL to the serialized inference embeddings. Defaults to None.
            inferences (Optional[Inferences], optional): The inferences to upload.
            wait_until_finish (bool, optional): Block until the dataset processing job finishes. This generally takes at least 5 minutes, and scales with the size of the dataset. Does not work in streaming pipeline mode. Defaults to False.
            wait_timeout (datetime.timedelta, optional): Maximum time to wait for. Defaults to 2 hours.
            embedding_distance_metric (str, optional): Distance metric to use for embedding layout. Can be a member of ['euclidean', 'cosine']. Defaults to 'euclidean'.
            delete_cache_files_after_upload (bool, optional): flag to turn off automatic deletion of cache files after upload. Useful for ipython notebook users that reload/re-attempt uploads. Defaults to True.
            external_metadata (Optional[Dict[str, Any]], optional): A JSON object that can be used to attach metadata to the inferences itself
            pipeline_mode (str, optional): BATCH or STREAMING
        """

        return self.create_or_update_inferences(
            project_id,
            dataset_id,
            inferences_id,
            data_url=data_url,
            embeddings_url=embeddings_url,
            inferences=inferences,
            wait_until_finish=wait_until_finish,
            wait_timeout=wait_timeout,
            embedding_distance_metric=embedding_distance_metric,
            delete_cache_files_after_upload=delete_cache_files_after_upload,
            external_metadata=external_metadata,
            pipeline_mode=pipeline_mode,
        )

    # Even though this is the same implementation as `update_dataset_metadata`, we split it out
    # because users have been working with inference-specific functions
    def update_inferences_metadata(
        self, project_id: str, inferences_id: str, external_metadata: Dict[str, Any]
    ) -> None:
        """Update inference set metadata

        Args:
            project_id (str): The project id.
            inferences_id (str): The inferences id.
            external_metadata (Dict[Any, Any]): The new metadata
        """
        if not isinstance(external_metadata, dict) or (
            external_metadata and not isinstance(next(iter(external_metadata)), str)
        ):
            raise Exception("external_metadata must be a dict with string keys")

        payload = {"external_metadata": external_metadata}
        r = requests_retry.post(
            f"{self.api_endpoint}/projects/{project_id}/datasets/{inferences_id}/metadata",
            headers=self._get_creds_headers(),
            json=payload,
        )
        raise_resp_exception_error(r)

    def _rehydrate_frame_user_metadata(
        self, frame: LabeledFrame, metadata: Dict[str, Any]
    ) -> LabeledFrame:
        for key, value in metadata.items():
            if isinstance(value, (list, tuple)):
                frame.add_user_metadata_list(key, cast(USER_METADATA_SEQUENCE, value))
            else:
                frame.add_user_metadata(key, value)
        return frame

    def _rehydrate_frame_object(
        self, frame_dict: Dict[str, Any], include_user_metadata: bool = True
    ) -> LabeledFrame:
        """Recreated a labeled frame object from Dict

        Returns:
            LabeledFrame
        """
        pipeline_keys = ["_idx", "window", "table", "reuse_latest_embedding"]
        app_keys = ["issues"]
        for key in pipeline_keys:
            frame_dict.pop(key, None)
        for key in app_keys:
            frame_dict.pop(key, None)

        frame_id = frame_dict.pop("task_id")
        date_captured = frame_dict.pop("date_captured")
        device_id = frame_dict.pop("device_id")
        labeled_frame = LabeledFrame(
            frame_id=frame_id,
            date_captured=date_captured,
            device_id=device_id,
            reuse_latest_embedding=True,
        )
        coordinate_frames = frame_dict.pop("coordinate_frames")
        sensor_data = frame_dict.pop("sensor_data")
        label_data = frame_dict.pop("label_data")
        geo_data = frame_dict.pop("geo_data", "{}")
        user_metadata = split_user_attrs(frame_dict)
        for key in user_metadata:
            frame_dict.pop(key, None)

        # warn if there are more fields left in the frame
        if frame_dict:
            keys = ",".join(list(frame_dict.keys()))
            print(
                f"WARNING! Rehydrating a frame resulted in unexpected unused keys: {keys}"
            )
            print("Please reach out to Aquarium if this occurs.")

        try:
            geo_data = json.loads(geo_data)
        except:
            pass

        # shoe-horn directly into the frame
        for sensor in sensor_data:
            labeled_frame.sensor_data.append(maybe_parse_json_vals(sensor))
        for label in label_data:
            label_dict = maybe_parse_json_vals(label)
            for key in pipeline_keys:
                label_dict.pop(key, None)
            labeled_frame._labels.label_data.append(
                cast(BaseLabelEntryDict, label_dict)
            )
        for coordinate_frame in coordinate_frames:
            labeled_frame._add_coordinate_frame(maybe_parse_json_vals(coordinate_frame))
        if geo_data:
            labeled_frame.geo_data = geo_data

        if include_user_metadata:
            labeled_frame = self._rehydrate_frame_user_metadata(
                labeled_frame, user_metadata
            )

        return labeled_frame

    def get_frame_ids(self, project_id: str, dataset_id: str) -> List[str]:
        """Get frame ids in a dataset (for datasets only, not inferences)

        Args:
            project_id (str): The project id.
            dataset_id (str): The dataset id.
        """
        r = requests_retry.get(
            f"{self.api_endpoint}/projects/{project_id}/datasets/{dataset_id}/frame_ids/LATEST",
            headers=self._get_creds_headers(),
        )

        raise_resp_exception_error(r)
        result: List[str] = r.json()
        return result

    def get_frame(
        self, project_id: str, dataset_id: str, frame_id: str
    ) -> LabeledFrame:
        """Get frame info (for datasets only, not inferences)

        Args:
            project_id (str): The project id.
            dataset_id (str): The dataset id.
            frame_id (str): The frame id.
        """
        r = requests_retry.get(
            f"{self.api_endpoint}/projects/{project_id}/datasets/{dataset_id}/frame/{frame_id}/LATEST",
            headers=self._get_creds_headers(),
        )

        raise_resp_exception_error(r)
        result: Dict[str, Any] = r.json()
        result_frame = self._rehydrate_frame_object(result)
        return result_frame

    def get_frames(
        self, project_id: str, dataset_id: str, frame_ids: List[str]
    ) -> Dict[str, LabeledFrame]:
        """Get multple frame infos (for datasets only, not inferences)

        Args:
            project_id (str): The project id.
            dataset_id (str): The dataset id.
            frame_ids (List[str]): The list of frame ids.
        """
        frames_r = requests_retry.post(
            f"{self.api_endpoint}/projects/{project_id}/datasets/{dataset_id}/frames/LATEST",
            headers=self._get_creds_headers(),
            json={"frame_ids": frame_ids},
        )
        raise_resp_exception_error(frames_r)
        result: List[Dict[str, Any]] = frames_r.json()
        return {f["task_id"]: self._rehydrate_frame_object(f) for f in result}

    def update_frames_metadata(
        self,
        project_id: str,
        dataset_id: str,
        frame_metadata_updates: Dict[str, Any],
    ) -> None:
        """Update the external metadata for labeled frames

        Args:
            project_id (str): The project id.
            dataset_id (str): The dataset id.
            frame_metadata_updates (Dict[str, Dict[str, Any]]): dictionary of frame_id to dictionary of metadata fields to change
        """
        frames_r = requests_retry.post(
            f"{self.api_endpoint}/projects/{project_id}/datasets/{dataset_id}/frames/LATEST",
            headers=self._get_creds_headers(),
            json={
                "frame_ids": list(frame_metadata_updates.keys()),
            },
        )
        raise_resp_exception_error(frames_r)
        result: List[Dict[str, Any]] = frames_r.json()

        appending_dataset = LabeledDataset(pipeline_mode="STREAMING")

        for frame in result:
            frame_id = frame["task_id"]
            user_metadata = split_user_attrs(frame)
            updated_frame = self._rehydrate_frame_object(
                frame, include_user_metadata=False
            )

            updated_metadata = frame_metadata_updates[frame_id]
            for key, value in updated_metadata.items():
                existing_key = f"user__{key}" if "user__" not in key else key
                existing_value = user_metadata.get(existing_key, None)
                new_value_is_listish = isinstance(value, (list, tuple))

                if existing_value == None:
                    if isinstance(value, (list, tuple)):
                        updated_frame.add_user_metadata_list(
                            key, cast(USER_METADATA_SEQUENCE, value)
                        )
                    else:
                        updated_frame.add_user_metadata(key, value)
                    continue

                existing_value_is_listish = isinstance(existing_value, (list, tuple))

                # verify that new value is of similar type to old value
                if existing_value_is_listish and not new_value_is_listish:
                    raise Exception(
                        f"New value for {key} for frame {frame_id} is not a list or tuple, but the existing value is; updates must be of the same type"
                    )

                if not existing_value_is_listish and new_value_is_listish:
                    raise Exception(
                        f"New value for {key} for frame {frame_id} is a list or tuple, but the existing value is not; updates must be of the same type"
                    )

                if new_value_is_listish:
                    found_val_types = {type(el) for el in value}
                    if len(found_val_types) > 1:
                        raise Exception(
                            f"New value for {key} for frame {frame_id} has elements of invalid type."
                            f"Expected all elements to be of the same type, found types of {found_val_types}"
                        )

                if value and existing_value:
                    # make sure types match
                    test_new_value = value[0] if new_value_is_listish else value
                    test_existing_value = (
                        existing_value[0]
                        if existing_value_is_listish
                        else existing_value
                    )

                    if type(test_existing_value) is not type(test_new_value):
                        raise Exception(
                            f"New value for {key} for frame {frame_id} does not match the existing value's type; expected {type(test_existing_value)} but saw {type(test_new_value)}; updates must be of the same type"
                        )

                user_metadata[existing_key] = value

            for key, value in user_metadata.items():
                if bool(value):
                    # if nullish, allow BQ set default type rather than inferring client-side
                    if isinstance(value, (list, tuple)):
                        updated_frame.add_user_metadata_list(
                            key, cast(USER_METADATA_SEQUENCE, value)
                        )
                    else:
                        updated_frame.add_user_metadata(key, value)

            appending_dataset.add_frame(updated_frame)

        self.add_to_streaming_dataset(
            project_id, dataset_id, appending_dataset, reuse_embeddings=True
        )

    def update_dataset_object_metadata_schema(
        self,
        project_id: str,
        dataset_id: str,
        object_metadata_fields: List[Dict[str, str]],
    ) -> None:
        """Update dataset object metadata schema

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id
            object_metadata_fields (List[Dict[str, Any]]): list of object metadata fields, formatted {"name": "width_bucket", "type": "STRING"}
                Type must be one of STRING, BOOL, NUMERIC, INTEGER, FLOAT, or an array of a valid type ARRAY<type>.
        """
        endpoint = (
            self.api_endpoint
            + "/projects/{}/datasets/{}/object_metadata_schema".format(
                project_id, dataset_id
            )
        )
        payload = {"schema": object_metadata_fields}
        r = requests_retry.post(
            endpoint,
            headers=self._get_creds_headers(),
            json=payload,
        )
        raise_resp_exception_error(r)
        print("Object metadata schema updated.")

    def get_dataset_object_metadata_schema(
        self, project_id: str, dataset_id: str
    ) -> List[Dict[str, str]]:
        """Get dataset object metadata schema

        Args:
            project_id (str): project_id
            dataset_id (str): dataset_id
        """
        endpoint = (
            self.api_endpoint
            + "/projects/{}/datasets/{}/object_metadata_schema".format(
                project_id, dataset_id
            )
        )
        r = requests_retry.get(
            endpoint,
            headers=self._get_creds_headers(),
        )
        raise_resp_exception_error(r)
        result: List[Dict[str, str]] = r.json()
        return result
