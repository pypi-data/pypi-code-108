import json
from typing import Optional, Dict
from uuid import UUID

import click

from montecarlodata.common.data import MonolithResponse
from montecarlodata.config import Config
from montecarlodata.errors import manage_errors
from montecarlodata.integrations.onboarding.base import BaseOnboardingService
from montecarlodata.integrations.onboarding.fields import EXPECTED_UPDATE_CREDENTIALS_RESPONSE_FIELD, \
    EXPECTED_REMOVE_CONNECTION_RESPONSE_FIELD, OPERATION_ERROR_VERBIAGE, EXPECTED_TEST_EXISTING_RESPONSE_FIELD
from montecarlodata.queries.onboarding import UPDATE_CREDENTIALS_MUTATION, REMOVE_CONNECTION_MUTATION, \
    TEST_EXISTING_CONNECTION_QUERY


class ConnectionOperationsService(BaseOnboardingService):
    REMOVE_PROMPT = 'Are you sure? This action deletes any associated jobs, monitors, etc.'

    def __init__(self, config: Config, **kwargs):
        super().__init__(config, **kwargs)

    @manage_errors
    def update_credentials(
        self,
        connection_id: UUID,
        changes: Dict,
        should_validate: Optional[bool] = True,
        should_replace: Optional[bool] = False
    ) -> None:
        """
        Update credentials for a connection
        """
        self.echo_operation_status(
            self._request_wrapper.make_request_v2(
                query=UPDATE_CREDENTIALS_MUTATION,
                operation=EXPECTED_UPDATE_CREDENTIALS_RESPONSE_FIELD,
                variables=dict(connection_id=str(connection_id), changes=json.dumps(changes),
                               should_validate=should_validate, should_replace=should_replace)
            ),
            operation=f'Updated \'{connection_id}\'.'
        )

    @manage_errors
    def remove_connection(self, connection_id: UUID, no_prompt: Optional[bool] = False) -> None:
        """
        Remove connection by ID. Deletes any associated jobs
        """
        if no_prompt or click.confirm(self.REMOVE_PROMPT, abort=True):
            self.echo_operation_status(
                self._request_wrapper.make_request_v2(
                    query=REMOVE_CONNECTION_MUTATION,
                    operation=EXPECTED_REMOVE_CONNECTION_RESPONSE_FIELD,
                    variables=dict(connection_id=str(connection_id))
                ),
                operation=f'Removed \'{connection_id}\'.'
            )

    @manage_errors
    def echo_test_existing(self, connection_id: UUID) -> None:
        """
        Tests an existing connection and echos results in pretty JSON
        """
        response = self._request_wrapper.make_request_v2(
            query=TEST_EXISTING_CONNECTION_QUERY,
            operation=EXPECTED_TEST_EXISTING_RESPONSE_FIELD,
            variables=dict(connection_id=connection_id)
        )
        click.echo(json.dumps(response.data, indent=4, ensure_ascii=False))

    @staticmethod
    def echo_operation_status(response: MonolithResponse, operation: str) -> None:
        """
        Echos operation status. Expects response contains a 'success' field as per API signature
        """
        if response.data.get('success'):
            click.echo(f'Success! {operation}')
        else:
            # Any errors thrown by the API are captured and handled in the request
            # lib/caller deco (e.g. validation errors). This should only reachable for invalid inputs for the account
            click.echo(OPERATION_ERROR_VERBIAGE)
