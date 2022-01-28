import click

from montecarlodata.common.common import read_as_base64
from montecarlodata.config import Config
from montecarlodata.errors import manage_errors, prompt_connection, complain_and_abort
from montecarlodata.integrations.onboarding.base import BaseOnboardingService
from montecarlodata.integrations.onboarding.fields import EXPECTED_TEST_TABLEAU_RESPONSE_FIELD, \
    CONFIRM_CONNECTION_VERBIAGE, CONNECTION_TEST_SUCCESS_VERBIAGE, CONNECTION_TEST_FAILED_VERBIAGE, \
    SKIP_ADD_CONNECTION_VERBIAGE, EXPECTED_ADD_TABLEAU_RESPONSE_FIELD, ADD_CONNECTION_SUCCESS_VERBIAGE, \
    ADD_CONNECTION_FAILED_VERBIAGE, EXPECTED_LOOKER_METADATA_RESPONSE_FIELD, LOOKER_MD_CONNECTION_TYPE, \
    EXPECTED_ADD_BI_RESPONSE_FIELD, EXPECTED_LOOKER_GIT_CLONE_RESPONSE_FIELD, LOOKER_GIT_CLONE_CONNECTION_TYPE
from montecarlodata.queries.onboarding import TEST_TABLEAU_CRED_MUTATION, ADD_TABLEAU_CONNECTION_MUTATION, \
    TEST_LOOKER_METADATA_CRED_MUTATION, ADD_BI_CONNECTION_MUTATION, TEST_LOOKER_GIT_CLONE_CRED_MUTATION


class ReportsOnboardingService(BaseOnboardingService):
    def __init__(self, config: Config, **kwargs):
        super().__init__(config, **kwargs)

    @manage_errors
    def onboard_tableau(self, **kwargs) -> None:
        """
        Onboard a tableau connection
        """
        connection_options = self._build_connection_options(**kwargs)
        response = self._request_wrapper.make_request_v2(
            query=TEST_TABLEAU_CRED_MUTATION,
            operation=EXPECTED_TEST_TABLEAU_RESPONSE_FIELD,
            variables=connection_options.monolith_base_payload
        )
        if response.data.success:
            click.echo(CONNECTION_TEST_SUCCESS_VERBIAGE)
        else:
            complain_and_abort(CONNECTION_TEST_FAILED_VERBIAGE)

        if not connection_options.validate_only:
            if connection_options.dc_id:
                connection_options.monolith_base_payload['dc_id'] = connection_options.dc_id

            prompt_connection(message=CONFIRM_CONNECTION_VERBIAGE, skip_prompt=connection_options.auto_yes)
            response = self._request_wrapper.make_request_v2(
                query=ADD_TABLEAU_CONNECTION_MUTATION,
                operation=EXPECTED_ADD_TABLEAU_RESPONSE_FIELD,
                variables=connection_options.monolith_base_payload
            )
            if response.data.tableauAccount.uuid:
                click.echo(f'{ADD_CONNECTION_SUCCESS_VERBIAGE}tableau.')
            else:
                complain_and_abort(ADD_CONNECTION_FAILED_VERBIAGE)
        else:
            click.echo(SKIP_ADD_CONNECTION_VERBIAGE)

    @manage_errors
    def onboard_looker_metadata(self, **kwargs) -> None:
        """
        Onboard a looker metadata connection
        """
        self.onboard(validation_query=TEST_LOOKER_METADATA_CRED_MUTATION,
                     validation_response=EXPECTED_LOOKER_METADATA_RESPONSE_FIELD,
                     connection_query=ADD_BI_CONNECTION_MUTATION,
                     connection_response=EXPECTED_ADD_BI_RESPONSE_FIELD,
                     connection_type=LOOKER_MD_CONNECTION_TYPE, **kwargs)

    @manage_errors
    def onboard_looker_git(self, **kwargs) -> None:
        """
        Onboard a looker git ssh connection
        """
        if kwargs.get('ssh_key'):
            kwargs['ssh_key'] = read_as_base64(kwargs.pop('ssh_key')).decode('utf-8')
        self.onboard(validation_query=TEST_LOOKER_GIT_CLONE_CRED_MUTATION,
                     validation_response=EXPECTED_LOOKER_GIT_CLONE_RESPONSE_FIELD,
                     connection_query=ADD_BI_CONNECTION_MUTATION,
                     connection_response=EXPECTED_ADD_BI_RESPONSE_FIELD,
                     connection_type=LOOKER_GIT_CLONE_CONNECTION_TYPE, **kwargs)
