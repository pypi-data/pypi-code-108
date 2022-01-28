import json
from typing import Optional, Dict

from montecarlodata.iac.schemas import ConfigTemplateUpdateResponse, ConfigTemplateDeleteResponse
from montecarlodata.queries.iac import CREATE_OR_UPDATE_MONTE_CARLO_CONFIG_TEMPLATE, DELETE_MONTE_CARLO_CONFIG_TEMPLATE
from montecarlodata.utils import GqlWrapper


class MonteCarloConfigTemplateClient:
    def __init__(self, gql_wrapper: GqlWrapper):
        self._gql_wrapper = gql_wrapper

    def apply_config_template(self,
                              namespace: str,
                              config_template_as_dict: Dict,
                              resource: Optional[str] = None,
                              dry_run: bool = False) -> ConfigTemplateUpdateResponse:
        response = self._gql_wrapper.make_request_v2(
            query=CREATE_OR_UPDATE_MONTE_CARLO_CONFIG_TEMPLATE,
            operation='createOrUpdateMonteCarloConfigTemplate',
            variables=dict(
                namespace=namespace,
                configTemplateJson=json.dumps(config_template_as_dict),
                dryRun=dry_run,
                resource=resource
            )
        )

        return ConfigTemplateUpdateResponse.from_dict(response.data['response'])

    def delete_config_template(self,
                               namespace: str,
                               dry_run: bool = False) -> ConfigTemplateDeleteResponse:
        response = self._gql_wrapper.make_request_v2(
            query=DELETE_MONTE_CARLO_CONFIG_TEMPLATE,
            operation='deleteMonteCarloConfigTemplate',
            variables=dict(
                namespace=namespace,
                dryRun=dry_run,
            )
        )

        return ConfigTemplateDeleteResponse.from_dict(response.data['response'])
