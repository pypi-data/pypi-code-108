from typing import Iterable, List, Optional

from benchling_api_client.api.lab_automation import (
    archive_automation_output_processors,
    create_automation_output_processor,
    generate_input_with_automation_input_generator,
    get_automation_input_generator,
    get_automation_output_processor,
    get_lab_automation_transform,
    list_automation_output_processors,
    process_output_with_automation_output_processor,
    unarchive_automation_output_processors,
    update_automation_input_generator,
    update_automation_output_processor,
    update_lab_automation_transform,
)
from benchling_api_client.types import Response

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset
from benchling_sdk.models import (
    AsyncTaskLink,
    AutomationInputGenerator,
    AutomationInputGeneratorUpdate,
    AutomationOutputProcessor,
    AutomationOutputProcessorArchivalChange,
    AutomationOutputProcessorCreate,
    AutomationOutputProcessorsArchive,
    AutomationOutputProcessorsArchiveReason,
    AutomationOutputProcessorsPaginatedList,
    AutomationOutputProcessorsUnarchive,
    AutomationOutputProcessorUpdate,
    LabAutomationTransform,
    LabAutomationTransformUpdate,
)
from benchling_sdk.services.base_service import BaseService


class LabAutomationService(BaseService):
    """
    Lab Automation.

    Lab Automation endpoints support integration with lab instruments, and liquid handlers to create samples or
    results, and capture transfers between containers at scale.

    See https://benchling.com/api/reference#/Lab%20Automation
    """

    @api_method
    def input_generator_by_id(self, input_generator_id: str) -> AutomationInputGenerator:
        """
        Get an Automation Input Generator.

        See https://benchling.com/api/reference#/Lab%20Automation/getAutomationInputGenerator
        """
        response = get_automation_input_generator.sync_detailed(
            client=self.client, input_generator_id=input_generator_id
        )
        return model_from_detailed(response)

    @api_method
    def update_input_generator(
        self, input_generator_id: str, file_id: Optional[str]
    ) -> AutomationInputGenerator:
        """
        Update an Automation Input Generator.

        See https://benchling.com/api/reference#/Lab%20Automation/updateAutomationInputGenerator
        """
        update = AutomationInputGeneratorUpdate(file_id=file_id)
        response = update_automation_input_generator.sync_detailed(
            client=self.client, input_generator_id=input_generator_id, json_body=update
        )
        return model_from_detailed(response)

    @api_method
    def output_processor_by_id(self, output_processor_id: str) -> AutomationOutputProcessor:
        """
        Get an Automation Output Processor.

        See https://benchling.com/api/reference#/Lab%20Automation/getAutomationOutputProcessor
        """
        response = get_automation_output_processor.sync_detailed(
            client=self.client, output_processor_id=output_processor_id
        )
        return model_from_detailed(response)

    @api_method
    def update_output_processor(self, output_processor_id: str, file_id: str) -> AutomationOutputProcessor:
        """
        Update an Automation Output Processor.

        See https://benchling.com/api/reference#/Lab%20Automation/updateAutomationOutputProcessor
        """
        update = AutomationOutputProcessorUpdate(file_id=file_id)
        response = update_automation_output_processor.sync_detailed(
            client=self.client, output_processor_id=output_processor_id, json_body=update
        )
        return model_from_detailed(response)

    @api_method
    def generate_input(self, input_generator_id: str) -> AsyncTaskLink:
        """
        Generate input with an Automation Input Generator.

        See https://benchling.com/api/reference#/Lab%20Automation/generateInputWithAutomationInputGenerator
        """
        response = generate_input_with_automation_input_generator.sync_detailed(
            client=self.client, input_generator_id=input_generator_id
        )
        return model_from_detailed(response)

    @api_method
    def process_output(self, output_processor_id: str) -> AsyncTaskLink:
        """
        Process output with an Automation Output Processor.

        See https://benchling.com/api/reference#/Lab%20Automation/processOutputWithAutomationOutputProcessor
        """
        response = process_output_with_automation_output_processor.sync_detailed(
            client=self.client, output_processor_id=output_processor_id
        )
        return model_from_detailed(response)

    @api_method
    def _automation_output_processors_page(
        self,
        assay_run_id: str,
        automation_file_config_name: Optional[str],
        archive_reason: Optional[str],
        modified_at: Optional[str],
        next_token: NextToken = None,
    ) -> Response[AutomationOutputProcessorsPaginatedList]:
        return list_automation_output_processors.sync_detailed(  # type: ignore
            client=self.client,
            assay_run_id=assay_run_id,
            next_token=none_as_unset(next_token),
            automation_file_config_name=none_as_unset(automation_file_config_name),
            archive_reason=none_as_unset(archive_reason),
            modified_at=none_as_unset(modified_at),
        )

    def automation_output_processors(
        self,
        assay_run_id: str,
        automation_file_config_name: str = None,
        archive_reason: str = None,
        modified_at: Optional[str] = None,
    ) -> PageIterator[AutomationOutputProcessor]:
        """
        List non-empty Automation Output Processors.

        Only Automation Output Processors which have an attached file will be included.

        See https://benchling.com/api/reference#/Lab%20Automation/listAutomationOutputProcessors
        """

        def api_call(next_token: NextToken) -> Response[AutomationOutputProcessorsPaginatedList]:
            return self._automation_output_processors_page(
                assay_run_id=assay_run_id,
                next_token=next_token,
                automation_file_config_name=automation_file_config_name,
                archive_reason=archive_reason,
                modified_at=modified_at,
            )

        def results_extractor(
            body: AutomationOutputProcessorsPaginatedList,
        ) -> List[AutomationOutputProcessor]:
            return body.automation_output_processors

        return PageIterator(api_call, results_extractor)

    @api_method
    def create_output_processor(
        self, automation_output_processor: AutomationOutputProcessorCreate
    ) -> AutomationOutputProcessor:
        """
        Create an Automation Output Processor.

        See https://benchling.com/api/reference#/Lab%20Automation/createAutomationOutputProcessor
        """
        response = create_automation_output_processor.sync_detailed(
            client=self.client, json_body=automation_output_processor
        )
        return model_from_detailed(response)

    @api_method
    def archive_automation_output_processors(
        self, automation_output_processor_ids: Iterable[str], reason: AutomationOutputProcessorsArchiveReason
    ) -> AutomationOutputProcessorArchivalChange:
        """
        Archive Automation Output Processors.

        See https://benchling.com/api/reference#/Lab%20Automation/archiveAutomationOutputProcessors
        """
        archive_request = AutomationOutputProcessorsArchive(
            reason=reason, automation_output_processor_ids=list(automation_output_processor_ids)
        )
        response = archive_automation_output_processors.sync_detailed(
            client=self.client, json_body=archive_request
        )
        return model_from_detailed(response)

    @api_method
    def unarchive_automation_output_processors(
        self, automation_output_processor_ids: Iterable[str]
    ) -> AutomationOutputProcessorArchivalChange:
        """
        Unarchive Automation Output Processors.

        See https://benchling.com/api/reference#/Lab%20Automation/unarchiveAutomationOutputProcessors
        """
        unarchive_request = AutomationOutputProcessorsUnarchive(
            automation_output_processor_ids=list(automation_output_processor_ids)
        )
        response = unarchive_automation_output_processors.sync_detailed(
            client=self.client, json_body=unarchive_request
        )
        return model_from_detailed(response)

    # TODO Should we rename this model LabAutomationTransform?

    @api_method
    def get_transform_by_id(self, transform_id: str) -> LabAutomationTransform:
        """
        Get a Lab Automation Transform step.

        See https://benchling.com/api/reference#/Lab%20Automation/getLabAutomationTransform
        """
        response = get_lab_automation_transform.sync_detailed(client=self.client, transform_id=transform_id)
        return model_from_detailed(response)

    @api_method
    def update_transform(
        self, transform_id: str, update: LabAutomationTransformUpdate
    ) -> LabAutomationTransform:
        """
        Update a Lab Automation Transform step.

        See https://benchling.com/api/reference#/Lab%20Automation/patchLabAutomationTransform
        """
        response = update_lab_automation_transform.sync_detailed(
            client=self.client, transform_id=transform_id, json_body=update
        )
        return model_from_detailed(response)
