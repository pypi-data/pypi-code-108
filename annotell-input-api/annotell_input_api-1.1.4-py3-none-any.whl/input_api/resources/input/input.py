from annotell.input_api.model.input.input_entry import Input
import logging
from typing import List, Optional

import annotell.input_api.model.input as InputModel
from annotell.input_api.util import filter_none
from annotell.input_api.resources.abstract import InputAPIResource

log = logging.getLogger(__name__)


class InputResource(InputAPIResource):
    """
    Class exposing Annotell Inputs
    """

    def invalidate_inputs(self, input_uuids: List[str], invalidated_reason: InputModel.InvalidatedReasonInput) -> None:
        """
        Invalidates inputs, and removes them from all input lists

        :param input_uuids: The input uuids to invalidate
        :param invalidated_reason: An Enum describing why inputs were invalidated
        """
        invalidated_json = dict(inputIds=input_uuids, invalidatedReason=invalidated_reason)
        self._client.post("v1/inputs/actions/invalidate", json=invalidated_json, discard_response=True)

    def get_inputs(
        self,
        project: str,
        batch: Optional[str] = None,
        include_invalidated: bool = False,
        external_ids: Optional[List[str]] = None,
    ) -> List[InputModel.Input]:
        """
        Gets inputs for project, with option to filter for invalidated inputs

        :param project: Project (identifier) to filter
        :param batch: Batch (identifier) to filter
        :param invalidated: Returns invalidated inputs if True, otherwise valid inputs
        :param external_id: External ID to filter input on
        :return List: List of Inputs
        """

        external_id_query_param = ",".join(external_ids) if external_ids else None
        json_resp = self._client.get(
            "v1/inputs",
            params=filter_none(
                {"project": project, "batch": batch, "invalidated": include_invalidated, "externalIds": external_id_query_param}
            )
        )
        return [InputModel.Input.from_json(js) for js in json_resp]

    def add_annotation_type(self, input_uuid: str, annotation_type: str) -> None:
        """
        Adds annotation-type to the input, which informs the Annotell Platform
        to produce a corresponding annotation for the annotation-type. Only
        possible if the annotation-type is available in the corresponding batch
        of the input (use method `get_annotation_types` to check).
        """

        self._client.post(f"v1/inputs/{input_uuid}/actions/add-annotation-type/{annotation_type}", discard_response=True)

    def get_inputs_by_uuids(self, input_uuids: List[str]) -> List[Input]:
        """
        Gets inputs using input uuids

        :param input_uuids: A UUID to filter inputs on
        :return List: List of Inputs
        """

        body = dict(uuids=input_uuids)
        json_resp = self._client.post("v1/inputs/query", json=body)
        return [Input.from_json(js) for js in json_resp]
