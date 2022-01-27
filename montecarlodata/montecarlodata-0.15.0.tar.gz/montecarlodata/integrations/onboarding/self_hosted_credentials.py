from montecarlodata.common.data import AWSArn
from montecarlodata.errors import complain_and_abort, manage_errors
from montecarlodata.integrations.onboarding.base import BaseOnboardingService
from montecarlodata.integrations.onboarding.fields import (
    CONNECTION_TO_WAREHOUSE_TYPE_MAP,
    EXPECTED_ADD_BI_RESPONSE_FIELD,
    EXPECTED_SELF_HOSTED_GQL_RESPONSE_FIELD,
    LOOKER_GIT_CLONE_CONNECTION_TYPE,
    LOOKER_MD_CONNECTION_TYPE,
)
from montecarlodata.queries.onboarding import (
    ADD_BI_CONNECTION_MUTATION,
    TEST_SELF_HOSTED_CRED_MUTATION,
)


class SelfHostedCredentialOnboardingService(BaseOnboardingService):
    BI_CONNECTION_TYPES = {LOOKER_GIT_CLONE_CONNECTION_TYPE, LOOKER_MD_CONNECTION_TYPE}

    @manage_errors
    def onboard_connection(self, connection_type: str, self_hosting_key: str, **kwargs) -> None:
        """
        Onboard a connection with self-hosted credentials by validating and adding a connection
        """
        kwargs['connectionType'] = connection_type

        try:
            region = AWSArn(self_hosting_key).region
        except IndexError:
            raise complain_and_abort('Credential key is not a valid ARN')

        if connection_type in CONNECTION_TO_WAREHOUSE_TYPE_MAP:
            kwargs['warehouseType'] = CONNECTION_TO_WAREHOUSE_TYPE_MAP[connection_type]
        elif connection_type in self.BI_CONNECTION_TYPES:
            kwargs['connection_query'] = ADD_BI_CONNECTION_MUTATION
            kwargs['connection_response'] = EXPECTED_ADD_BI_RESPONSE_FIELD

        self.onboard(
            validation_query=TEST_SELF_HOSTED_CRED_MUTATION,
            validation_response=EXPECTED_SELF_HOSTED_GQL_RESPONSE_FIELD,
            connection_type=connection_type,
            self_hosting_key=self_hosting_key,
            region=region,
            **kwargs
        )
