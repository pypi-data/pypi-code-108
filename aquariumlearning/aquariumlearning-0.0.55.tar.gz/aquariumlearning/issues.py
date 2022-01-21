"""issues.py
============
Functionality related to issue management
"""

import requests
from collections.abc import Iterable
from .util import raise_resp_exception_error, ElementType
from typing import Any, Union, List, Dict, Optional, TYPE_CHECKING
from typing_extensions import Literal, TypedDict

if TYPE_CHECKING:
    from .client import Client


# TODO: Find a way to reduce duplication
IssueState = Literal[
    "triage",
    "labeling_campaign_active",
    "inProgress",
    "inReview",
    "resolved",
    "ignored",
    "backlog",
    "cancelled",
]
all_issue_states: List[IssueState] = [
    "triage",
    "labeling_campaign_active",
    "inProgress",
    "inReview",
    "resolved",
    "ignored",
    "backlog",
    "cancelled",
]


class IssueElement:
    """Definition for issue element.

    Args:
        element_id (str): The element id.
        frame_id (str): The frame id of the element.
        element_type (str): The element type of the issue element ("frame" or "crop").
        dataset (str): The base dataset an element is from. (Can be formatted as either "project_name.dataset_name" or just "dataset_name")
        inference_set (str): The inference set an element is from (if any). (Can be formatted as either "project_name.inference_set_name" or just "inference_set_name")
        status (str): (*For read purposes, not element modification*). The status of the element.
        frame_data: (*For read purposes, not element modification*). JSON object that is based on either a LabeledFrame or InferencesFrame
        crop_data: (*For read purposes, not element modification*). JSON object for the specific "frame_data" crop that a "crop"-type element is based on.
        label_metadata: (*For read purposes, not element modification*). JSON object with confidence and IOU info if the element was created from a ground truth/inference comparison.
    """

    def __init__(
        self,
        element_id: str,
        frame_id: str,
        element_type: str,
        dataset: str,
        status: Optional[str] = None,
        inference_set: Optional[str] = None,
        # TODO: Type these three objects
        frame_data: Optional[Dict[str, Any]] = None,
        crop_data: Optional[Dict[str, Any]] = None,
        label_metadata: Optional[Dict[str, Any]] = None,
        comments: Optional[Dict[str, Any]] = None,
    ):
        if element_type != "crop" and element_type != "frame":
            raise Exception('element_type must be either "crop" or "frame"')

        self.element_id = element_id
        self.frame_id = frame_id
        self.element_type = element_type
        self.status = status
        self.dataset = dataset
        self.inference_set = inference_set
        self.frame_data = frame_data
        self.crop_data = crop_data
        self.label_metadata = label_metadata
        self.comments = comments

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_id": self.element_id,
            "frame_id": self.frame_id,
            "element_type": self.element_type,
            "status": self.status,
            "dataset": self.dataset,
            "inference_set": self.inference_set,
            "frame_data": self.frame_data,
            "crop_data": self.crop_data,
            "label_metadata": self.label_metadata,
            "comments": self.comments,
        }

    # For element modification
    def _to_api_format(self, project_name: str) -> Dict[str, Any]:
        api_payload = {
            "id": self.element_id,
            "frameId": self.frame_id,
            "type": self.element_type,
        }

        dataset_address = (
            self.dataset
            if "." in self.dataset
            else ".".join([project_name, self.dataset])
        )
        api_payload["dataset"] = dataset_address

        if self.inference_set is not None:
            inference_set_address = (
                self.inference_set
                if "." in self.inference_set
                else ".".join([project_name, self.inference_set])
            )
            api_payload["inferenceSet"] = inference_set_address

        return api_payload


# TODO: Which of these are specifically optional?
# TODO: Are they optional (as in, Nullable), or are they missing keys?


class IssueElementApiResp(TypedDict):
    id: str
    frameId: str
    type: ElementType
    status: str  # TODO: Types
    dataset: str
    inferenceSet: Optional[str]
    frameData: Optional[Dict[str, Any]]
    cropData: Optional[Dict[str, Any]]
    labelMetadata: Optional[Dict[str, Any]]
    comments: Optional[Dict[str, Any]]


class IssueApiResp(TypedDict):
    id: str
    compare_dataset: Optional[str]
    dataset: Optional[str]
    name: str
    element_type: ElementType
    created_at: Optional[str]
    updated_at: Optional[str]
    reporter: Optional[str]
    assignee: Optional[str]
    state: Optional[IssueState]
    issue_id: Optional[str]
    elements: List[IssueElementApiResp]
    comments: Optional[Dict[str, Any]]
    template_type: Optional[str]
    custom_template_fields: Optional[Dict[str, Any]]


class Issue:
    """Definition for issue.

    Args:
        name (str): The issue name.
        dataset (Optional[str]): The dataset for this issue.
        elements (List[IssueElement]): The elements of the issue.
        element_type (str): The element type of the issue ("frame", "crop").
        created_at (str): The time of issue creation.
        updated_at (str): The time of last issue update.
        reporter (str): Email of issue creator.
        assignee (Optional[str], optional): Email of the person assigned the issue. Defaults to None.
        state (str): Current state of issue ("triage", "inProgress", "inReview", "resolved", "cancelled"). Defaults to "triage".
        issue_id (str): The issue id.
        inference_set (Optional[str], optional): The inference set for this issue. Defaults to None.
        template_type (Optional[str]): The template type for this issue. (read-only)
        custom_template_fields (Optional[Dict[str, Any]]): Custom fields associated with the issue template type. (read-only)
    """

    def __init__(
        self,
        name: str,
        dataset: Optional[str],
        elements: List[IssueElement],
        element_type: ElementType,
        # TODO: This used to say datetime, but it looks like it should be a str?
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        reporter: Optional[str] = None,
        assignee: Optional[str] = None,
        state: Optional[str] = None,
        issue_id: Optional[str] = None,
        inference_set: Optional[str] = None,
        comments: Optional[Dict[str, Any]] = None,
        template_type: Optional[str] = None,
        custom_template_fields: Optional[Dict[str, Any]] = None,
    ):

        self.name = name
        self.dataset = dataset
        self.elements = elements
        self.element_type = element_type
        self.created_at = created_at
        self.updated_at = updated_at
        self.reporter = reporter
        self.assignee = assignee
        self.state = state
        self.issue_id = issue_id
        self.inference_set = inference_set
        self.comments = comments
        self.template_type = template_type
        self.custom_template_fields = custom_template_fields

    def __repr__(self) -> str:
        return "Issue {} ({})".format(self.issue_id, self.name)

    def __str__(self) -> str:
        return "Issue {} ({})".format(self.issue_id, self.name)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "dataset": self.dataset,
            "elements": [x.to_dict() for x in self.elements],
            "element_type": self.element_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "reporter": self.reporter,
            "assignee": self.assignee,
            "state": self.state,
            "issue_id": self.issue_id,
            "inference_set": self.inference_set,
            "comments": self.comments,
            "template_type": self.template_type,
            "custom_template_fields": self.custom_template_fields,
        }


class IssueManager:
    """An issue manager for interacting with issues within a given project.

    Args:
        client (Client): An Aquarium Learning Python Client object.
        project_id (str): The project id associated with this manager.
    """

    def __init__(self, client: "Client", project_id: str) -> None:
        self.client = client
        self.project_id = project_id

    @staticmethod
    def _issue_from_api_resp(api_resp: IssueApiResp) -> Issue:
        # TODO: Hack because internal data model for issues is still dataset/compare dataset,
        # not dataset + inference set + other inference set.

        compare_dataset = api_resp.get("compare_dataset")
        raw_dataset = api_resp.get("dataset")
        dataset: Optional[str] = None
        inference_set: Optional[str] = None

        if compare_dataset and raw_dataset:
            dataset = compare_dataset.split(".")[1]
            inference_set = raw_dataset.split(".")[1]
        elif raw_dataset:
            dataset = raw_dataset.split(".")[1]
            inference_set = None
        else:  # in the case of an issue with no elements
            dataset = None
            inference_set = None

        elements = []
        for raw_el in api_resp.get("elements", []):
            # TODO: Is the change to explicit accesses vs nullable gets correct?
            elements.append(
                IssueElement(
                    element_id=raw_el["id"],
                    frame_id=raw_el["frameId"],
                    element_type=raw_el["type"],
                    dataset=raw_el["dataset"],
                    status=raw_el.get("status"),
                    inference_set=raw_el.get("inferenceSet"),
                    frame_data=raw_el.get("frameData"),
                    crop_data=raw_el.get("cropData"),
                    label_metadata=raw_el.get("labelMetadata"),
                    comments=raw_el.get("comments"),
                )
            )

        # TODO: Is the change to explicit accesses vs nullable gets correct?
        return Issue(
            name=api_resp["name"],
            element_type=api_resp["element_type"],
            created_at=api_resp.get("created_at"),
            updated_at=api_resp.get("updated_at"),
            reporter=api_resp.get("reporter"),
            assignee=api_resp.get("assignee"),
            state=api_resp.get("state"),
            issue_id=api_resp["id"],
            comments=api_resp.get("comments"),
            dataset=dataset,
            inference_set=inference_set,
            elements=elements,
            template_type=api_resp.get("template_type"),
            custom_template_fields=api_resp.get("custom_template_fields"),
        )

    def add_elements_to_issue(
        self, issue_id: str, elements: List[IssueElement]
    ) -> None:
        """Add elements to an issue.

        Args:
            issue_id (str): The issue id.
            elements (List[IssueElement]): The elements to add to the issue.
        """
        if not isinstance(elements, Iterable):
            raise Exception("elements must be an iterable of IssueElement")

        # Validate contents of iterables:
        element_type_set = set()
        for element in elements:
            if not isinstance(element, IssueElement):
                raise Exception("elements must be an iterable of IssueElement")
            element_type_set.add(element.element_type)

        if len(element_type_set) != 1:
            raise Exception("Elements must contain exactly one element type")

        element_type = next(iter(element_type_set))
        payload = {
            "element_type": element_type,
            "elements": [x._to_api_format(self.project_id) for x in elements],
            "edit_type": "add",
        }

        url = "/projects/{}/issues/{}/elements".format(self.project_id, issue_id)
        r = requests.patch(
            self.client.api_endpoint + url,
            headers=self.client._get_creds_headers(),
            json=payload,
        )

        raise_resp_exception_error(r)

    def remove_elements_from_issue(
        self, issue_id: str, elements: List[IssueElement]
    ) -> None:
        """Remove elements from an issue.

        Args:
            issue_id (str): The issue id.
            elements (List[IssueElement]): The elements to remove from the issue.
        """
        if not isinstance(elements, Iterable):
            raise Exception("elements must be an iterable of IssueElement")

        # Validate contents of iterables:
        element_type_set = set()
        for element in elements:
            if not isinstance(element, IssueElement):
                raise Exception("elements must be an iterable of IssueElement")
            element_type_set.add(element.element_type)

        if len(element_type_set) != 1:
            raise Exception("Elements must contain exactly one element type")

        element_type = next(iter(element_type_set))
        payload = {
            "element_type": element_type,
            "elements": [x._to_api_format(self.project_id) for x in elements],
            "edit_type": "remove",
        }

        url = "/projects/{}/issues/{}/elements".format(self.project_id, issue_id)
        r = requests.patch(
            self.client.api_endpoint + url,
            headers=self.client._get_creds_headers(),
            json=payload,
        )

        raise_resp_exception_error(r)

    def list_issues(self) -> List[Issue]:
        """List issues in the associated project.

        NOTE: this does NOT include the `frame_data` or `crop_data` information for the issue elements.
        (Use `get_issue` instead to see that info).

        Returns:
            List[Issue]: List of all issues data.
        """
        url = "/projects/{}/issues".format(self.project_id)
        r = requests.get(
            self.client.api_endpoint + url, headers=self.client._get_creds_headers()
        )

        raise_resp_exception_error(r)
        return [self._issue_from_api_resp(x) for x in r.json()]

    def create_issue(
        self,
        name: str,
        dataset: str,
        elements: List[IssueElement],
        element_type: ElementType,
        inference_set: Optional[str] = None,
    ) -> str:
        """Create an issue.

        Args:
            name (str): The issue name.
            dataset (str): The dataset for this issue.
            elements (List[IssueElement]): The initial elements of the issue.
            element_type (str): The element type of the issue ("frame" or "crop").
            inference_set (Optional[str], optional): The inference set for this issue. Defaults to None.
        Returns:
            str: The created issue id.
        """
        if not isinstance(name, str):
            raise Exception("Issue names must be strings")

        if not self.client.dataset_exists(self.project_id, dataset):
            raise Exception("Dataset {} does not exist".format(dataset))

        if inference_set is not None:
            if not self.client.dataset_exists(self.project_id, inference_set):
                raise Exception("Inference set {} does not exist".format(inference_set))

        if element_type != "frame" and element_type != "crop":
            raise Exception('element type must be "frame" or "crop"')

        if not isinstance(elements, Iterable):
            raise Exception("elements must be an iterable of IssueElement")

        # Validate contents of iterables:
        for element in elements:
            if not isinstance(element, IssueElement):
                raise Exception("elements must be an iterable of IssueElement")
            if element.element_type != element_type:
                raise Exception(
                    "Child element {} has element type {} which conflicts with issue element type {}".format(
                        element.element_id, element.element_type, element_type
                    )
                )

        payload = {
            "name": name,
            "elements": [x._to_api_format(self.project_id) for x in elements],
            "element_type": element_type,
        }

        # TODO: Hack because internal data model for issues is still dataset/compare dataset,
        # not dataset + inference set + other inference set.

        if inference_set is None:
            payload["dataset"] = ".".join([self.project_id, dataset])
        else:
            payload["dataset"] = ".".join([self.project_id, inference_set])
            payload["compare_dataset"] = ".".join([self.project_id, dataset])

        url = "/projects/{}/issues".format(self.project_id)
        r = requests.post(
            self.client.api_endpoint + url,
            headers=self.client._get_creds_headers(),
            json=payload,
        )

        raise_resp_exception_error(r)
        resp_data: IssueApiResp = r.json()

        return resp_data["id"]

    def get_issue(
        self,
        issue_id: str,
        exclude_frame_data: bool = False,
        include_comment_data: bool = False,
    ) -> Issue:
        """Get a specific issue in the associated project.
        This will also include all associated frame metadata associated with each element.

        Args:
            issue_id (str): The issue id.
            exclude_frame_data (bool): Set to True to exclude full frame data from the issue element (e.g. to cut down on download size).
            include_comment_data (bool): Set to True to include comments on the issue and issue elements.

        Returns:
            Issue: The issue data (including frame_data, crop_data, label_metadata, and comments).
        """
        url = "/projects/{}/issues/{}/download_elements".format(
            self.project_id, issue_id
        )

        r = requests.get(
            self.client.api_endpoint + url,
            headers=self.client._get_creds_headers(),
            params={
                "get_as_gcs_file": True,
                "exclude_frame_data": exclude_frame_data,
                "include_comment_data": include_comment_data,
            },
        )

        raise_resp_exception_error(r)
        signed_url = r.json()["signed_url"]
        r = requests.get(signed_url)
        return self._issue_from_api_resp(r.json())

    def delete_issue(self, issue_id: str) -> None:
        """Delete an issue.

        Args:
            issue_id (str): The issue id.
        """
        url = "/projects/{}/issues/{}".format(self.project_id, issue_id)
        r = requests.delete(
            self.client.api_endpoint + url, headers=self.client._get_creds_headers()
        )

        raise_resp_exception_error(r)

    def update_issue_state(self, issue_id: str, issue_state: IssueState) -> None:
        """Update issue state.

        Args:
            issue_id (str): The issue id.
            issue_state (str): The new issue state. ("triage", "inProgress", "inReview", "resolved", "cancelled")
        """

        if not isinstance(issue_id, str):
            raise Exception("Issue id must be a string")

        if not isinstance(issue_state, str):
            raise Exception("Issue state must be a string")

        if issue_state not in all_issue_states:
            raise Exception("Invalid issue state")

        payload = {"state": issue_state}

        url = "/projects/{}/issues/{}/update_state".format(self.project_id, issue_id)
        r = requests.patch(
            self.client.api_endpoint + url,
            headers=self.client._get_creds_headers(),
            json=payload,
        )

        raise_resp_exception_error(r)

    def update_issue_name(self, issue_id: str, issue_name: str) -> None:
        """Update issue name.

        Args:
            issue_id (str): The issue id.
            issue_name (str): The new issue name.
        """

        if not isinstance(issue_id, str):
            raise Exception("Issue id must be a string")

        if not isinstance(issue_name, str):
            raise Exception("Issue name must be a string")

        payload = {"name": issue_name}

        url = "/projects/{}/issues/{}/rename".format(self.project_id, issue_id)
        r = requests.patch(
            self.client.api_endpoint + url,
            headers=self.client._get_creds_headers(),
            json=payload,
        )

        raise_resp_exception_error(r)

    def update_elements_status(
        self, issue_id: str, element_ids: List[str], new_status: str
    ) -> None:
        """Update issue elements status.

        Args:
            issue_id (str): The issue id.
            new_status (str): The new status. ("unstarted", "done")
        """

        payload = {
            "edit_type": "update",
            "element_type": None,
            "elements": [{"id": element_id} for element_id in element_ids],
            "new_status": new_status,
        }

        url = "/projects/{}/issues/{}/elements".format(self.project_id, issue_id)

        r = requests.patch(
            self.client.api_endpoint + url,
            headers=self.client._get_creds_headers(),
            json=payload,
        )

        raise_resp_exception_error(r)
