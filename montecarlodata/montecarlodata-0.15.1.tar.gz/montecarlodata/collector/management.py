import copy
from typing import Optional, Dict, List
from urllib import parse

import click
from tabulate import tabulate

from montecarlodata.collector.fields import EXPECTED_GENERATE_TEMPLATE_GQL_RESPONSE_FIELD, DEFAULT_COLLECTION_REGION, \
    EXPECTED_ADD_DC_RESPONSE_FIELD, ADD_DC_PROMPT_VERBIAGE, ADD_DC_REGION_PROMPT_VERBIAGE
from montecarlodata.common.user import UserService
from montecarlodata.config import Config
from montecarlodata.errors import manage_errors, complain_and_abort, prompt_connection
from montecarlodata.queries.collector import GENERATE_COLLECTOR_TEMPLATE, ADD_COLLECTOR_RECORD
from montecarlodata.utils import GqlWrapper, AwsClientWrapper


class CollectorManagementService:
    _DEFAULT_COLLECTOR_VAL = '-'
    _LIST_COLLECTOR_HEADERS = ['AWS Stack ARN', 'ID', 'Version', 'Last updated', 'Active']

    def __init__(self, config: Config, request_wrapper: Optional[GqlWrapper] = None,
                 aws_wrapper: Optional[AwsClientWrapper] = None, aws_profile_override: Optional[str] = None,
                 aws_region_override: Optional[str] = None, user_service: Optional[UserService] = None):
        self._abort_on_error = True
        self._collector_region = aws_region_override or config.aws_region or DEFAULT_COLLECTION_REGION

        self._request_wrapper = request_wrapper or GqlWrapper(mcd_id=config.mcd_id, mcd_token=config.mcd_token)
        self._aws_wrapper = aws_wrapper or AwsClientWrapper(profile_name=aws_profile_override or config.aws_profile,
                                                            region_name=self._collector_region)
        self._user_service = user_service or UserService(request_wrapper=self._request_wrapper, config=config)

    @manage_errors
    def echo_template(self, **kwargs) -> None:
        """
        Echos the most recent template for this account
        """
        click.echo(self._get_template_url_from_launch(self._get_template_launch_url(**kwargs)))

    @manage_errors
    def echo_collectors(self, headers: Optional[str] = 'firstrow', table_format: Optional[str] = 'fancy_grid',
                        active_only: Optional[bool] = False) -> None:
        """
        Echo collectors in a fancy grid.
        """
        table = [self._LIST_COLLECTOR_HEADERS]
        for collector in self._user_service.collectors or []:
            if active_only and not collector.get('active'):
                continue
            table.append(
                [
                    collector.get('stackArn') if collector.get('stackArn') else self._DEFAULT_COLLECTOR_VAL,
                    collector['uuid'],
                    collector.get('templateVersion') if collector.get('templateVersion') else self._DEFAULT_COLLECTOR_VAL,
                    collector.get('lastUpdated') if collector.get('lastUpdated') else self._DEFAULT_COLLECTOR_VAL,
                    collector.get('active')
                ]
            )
        click.echo(tabulate(table, headers=headers, tablefmt=table_format))

    @manage_errors
    def add_collector(self, no_prompt: Optional[bool] = False) -> None:
        """
        Add a collector to the account. Prompts to launch browser.
        """
        response = self._request_wrapper.make_request_v2(
            query=ADD_COLLECTOR_RECORD,
            operation=EXPECTED_ADD_DC_RESPONSE_FIELD,
        )
        dc_id = response.data.dc.uuid
        click.echo(f'Created collector record with ID \'{dc_id}\'')
        if no_prompt:
            return

        prompt_connection(message=ADD_DC_PROMPT_VERBIAGE)  # exits on No
        collection_region = click.prompt(
            ADD_DC_REGION_PROMPT_VERBIAGE,
            show_choices=True,
            default=DEFAULT_COLLECTION_REGION,
            show_default=True,
            type=click.Choice(self._user_service.active_collection_regions)
        )
        self.launch_quick_create_link(dry=False, dc_id=dc_id, collection_region=collection_region)

    @manage_errors
    def launch_quick_create_link(self, dry: Optional[bool] = True, **kwargs) -> None:
        """
        Open browser with a quick create link for deploying a data collector

        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-create-stacks-quick-create-links.html
        """
        launch_url = self._get_template_launch_url(**kwargs)
        if dry:
            click.echo(launch_url)
            return
        click.launch(launch_url)

    @manage_errors
    def upgrade_template(self, new_params: Optional[Dict] = None, **kwargs) -> None:
        """
        Upgrades the DC attached to this account
        """
        collector_details = self._generate_collector_template(**kwargs)
        try:
            stack_arn = collector_details['stackArn']
            is_active = collector_details['active']
            gateway_id = collector_details['apiGatewayId']
            template_url = self._get_template_url_from_launch(collector_details['templateLaunchUrl'])

            if not is_active:
                complain_and_abort('Cannot upgrade an inactive collector. Please contact Monte Carlo')
        except KeyError as err:
            complain_and_abort(f'Missing expected property ({err}). The collector may not have been deployed before')
        else:
            click.echo(f'Updating \'{stack_arn}\'')
            self._upgrade(stack_arn=stack_arn, template_url=template_url, gateway_id=gateway_id, new_params=new_params)
            click.echo('Upgrade complete! Have a nice day!')

    @manage_errors
    def deploy_template(self, stack_name: str, termination_protection: bool, new_params: Optional[Dict] = None,
                        **kwargs) -> None:
        """
        Deploys a template for this account
        """
        click.echo(f'Deploying \'{stack_name}\' in \'{self._collector_region}\'')
        collector_details = self._generate_collector_template(**kwargs)
        is_active = collector_details['active']
        if is_active:
            complain_and_abort('Cannot deploy with an already active collector.')

        template_url = self._get_template_url_from_launch(collector_details['templateLaunchUrl'])
        self._deploy(stack_name=stack_name, template_url=template_url, termination_protection=termination_protection,
                     new_params=new_params)

    def _upgrade(self, stack_arn: str, template_url: str, gateway_id: str, new_params: Dict) -> None:
        """
        Upgrade the collector stack and deploy the gateway
        """
        parameters = self._build_param_list(self._aws_wrapper.get_stack_parameters(stack_id=stack_arn), new_params)
        if self._aws_wrapper.upgrade_stack(stack_id=stack_arn, template_link=template_url, parameters=parameters):
            self._aws_wrapper.deploy_gateway(gateway_id=gateway_id)
        else:
            complain_and_abort('Failed to upgrade. Please review CF events for details')

    def _deploy(self, stack_name: str, template_url: str, termination_protection: bool,
                new_params: Optional[Dict] = None) -> None:
        """
        Deploy (create) a collector stack for the first time
        """
        parameters = self._build_param_list(existing_params=[], new_params=new_params)
        if not self._aws_wrapper.create_stack(stack_name=stack_name, template_link=template_url,
                                              termination_protection=termination_protection,
                                              parameters=parameters):
            complain_and_abort('Failed to deploy. Please review CF events for details')

    def _generate_collector_template(self, **kwargs) -> Optional[Dict]:
        """
        Generate the latest template and returns any associated dc properties (i.e. from the DataCollectorModel)
        """
        options = {'region': self._collector_region}
        if kwargs.get('collection_region'):
            options['region'] = kwargs['collection_region']  # overwrite client

        if kwargs.get('dc_id'):
            options['dc_id'] = kwargs['dc_id']

        response = self._request_wrapper.make_request_v2(
            query=GENERATE_COLLECTOR_TEMPLATE,
            operation=EXPECTED_GENERATE_TEMPLATE_GQL_RESPONSE_FIELD,
            variables=options
        )
        return response.data.get('dc')

    def _get_template_launch_url(self, **kwargs) -> str:
        """
        Get the template launch url
        """
        return self._generate_collector_template(**kwargs).get('templateLaunchUrl')

    @staticmethod
    def _get_template_url_from_launch(launch_url: str) -> str:
        """
        Extract the template url from expected launch url structure
        """
        return parse.parse_qs(parse.urlparse(launch_url).fragment).get('templateURL', [])[0]

    @staticmethod
    def _build_param_list(existing_params: List[Dict], new_params: Optional[Dict] = None) -> List[Dict]:
        """
        Get a list of parameters by replacing (or extending) any new params into the existing stack params
        """
        existing_params = copy.deepcopy(existing_params)
        new_params = copy.deepcopy(new_params)

        for param in existing_params or []:
            if new_params and new_params.get(param['ParameterKey']) is not None:
                param['ParameterValue'] = new_params[param['ParameterKey']]
                param['UsePreviousValue'] = False
                del new_params[param['ParameterKey']]
            else:
                del param['ParameterValue']
                param['UsePreviousValue'] = True
        if new_params:
            # Handle any completely new params (i.e. those that were not in the existing struct)
            # Can be found for params added between versions
            existing_params.extend([{'ParameterKey': k, 'ParameterValue': v} for k, v in new_params.items()])

        return existing_params
