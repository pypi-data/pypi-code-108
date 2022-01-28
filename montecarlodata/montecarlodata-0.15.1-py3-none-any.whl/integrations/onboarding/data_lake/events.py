from typing import Optional

import click

from montecarlodata.common.common import read_as_json_string
from montecarlodata.config import Config
from montecarlodata.errors import complain_and_abort, manage_errors
from montecarlodata.integrations.onboarding.base import BaseOnboardingService
from montecarlodata.integrations.onboarding.fields import EXPECTED_TOGGLE_EVENTS_GQL_RESPONSE_FIELD
from montecarlodata.queries.onboarding import TOGGLE_EVENT_MUTATION


class EventsOnboardingService(BaseOnboardingService):

    def __init__(self, config: Config, **kwargs):
        super().__init__(config, **kwargs)

    @manage_errors
    def toggle_event_configuration(self, **kwargs) -> Optional[bool]:
        """
        Toggle event configuration (effectively onboarding it if enable is set to true)
        """
        num_of_warehouses = len(self._user_service.warehouses)

        if num_of_warehouses == 1:
            kwargs['dwId'] = self._user_service.warehouses[0]['uuid']
            mapping_file = kwargs.pop('mapping_file', None)
            if mapping_file:
                kwargs['mapping'] = read_as_json_string(mapping_file)
            variables = self._request_wrapper.convert_snakes_to_camels(kwargs)
            status = self._request_wrapper.make_request(query=TOGGLE_EVENT_MUTATION, variables=variables).get(
                EXPECTED_TOGGLE_EVENTS_GQL_RESPONSE_FIELD, {}).get('success')
            if status:
                click.echo(f"Success! {'Enabled' if kwargs['enable'] else 'Disabled'} events.")
                return True
            complain_and_abort('Failed to toggle events!')
        complain_and_abort(f'Events only supports one warehouse. Found {num_of_warehouses}')
