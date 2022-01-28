import json
import os
from typing import Optional, Dict, List

import click
from tabulate import tabulate

from montecarlodata.common.data import ConnectionOptions, ValidationResult, OnboardingConfiguration
from montecarlodata.common.common import normalize_gql
from montecarlodata.common.user import UserService
from montecarlodata.config import Config
from montecarlodata.errors import complain_and_abort, prompt_connection
from montecarlodata.integrations.onboarding.fields import S3_CERT_MECHANISM, GQL_TO_FRIENDLY_CONNECTION_MAP, \
    DATA_LAKE_WAREHOUSE_TYPE, EXPECTED_ADD_CONNECTION_RESPONSE_FIELD, CONFIRM_CONNECTION_VERBIAGE, VALIDATIONS_FAILED_VERBIAGE, \
    SKIP_ADD_CONNECTION_VERBIAGE, CONNECTION_TEST_SUCCESS_VERBIAGE, CONNECTION_TEST_FAILED_VERBIAGE, \
    ADD_CONNECTION_FAILED_VERBIAGE, ADD_CONNECTION_SUCCESS_VERBIAGE
from montecarlodata.queries.onboarding import ADD_CONNECTION_MUTATION
from montecarlodata.utils import GqlWrapper, AwsClientWrapper


class BaseOnboardingService:
    _VALIDATION_STATUS_HEADERS = ['Validation', 'Result', 'Details']
    _VALIDATION_PASSED = 'Passed'
    _VALIDATION_FAILED = 'Failed'

    def __init__(self, config: Config, user_service: Optional[UserService] = None,
                 request_wrapper: Optional[GqlWrapper] = None,
                 aws_wrapper: Optional[AwsClientWrapper] = None):

        self._abort_on_error = True  # Aborts methods with deco on unhandled error
        self._dc_outputs = None

        self._user_service = user_service or UserService(config=config)
        self._request_wrapper = request_wrapper or GqlWrapper(mcd_id=config.mcd_id, mcd_token=config.mcd_token)
        self._aws_wrapper = aws_wrapper or AwsClientWrapper(profile_name=config.aws_profile,
                                                            region_name=config.aws_region)

    def onboard(self, **kwargs):
        """
        Convenience wrapper to validate and add a connection.
        """
        onboarding_config = OnboardingConfiguration(**kwargs)  # not passed as arg to avoid having to change all clients
        onboarding_config.connection_options = self._build_connection_options(**onboarding_config.connection_options)

        onboarding_config.warehouse_name = onboarding_config.connection_options.monolith_base_payload.pop('warehouseName', None)
        onboarding_config.warehouse_type = onboarding_config.connection_options.monolith_base_payload.pop('warehouseType', DATA_LAKE_WAREHOUSE_TYPE)

        result = self._validate_connection(
            query=onboarding_config.validation_query,
            response_field=onboarding_config.validation_response,
            **onboarding_config.connection_options.monolith_base_payload
        )

        if not onboarding_config.connection_options.validate_only:
            prompt = VALIDATIONS_FAILED_VERBIAGE if result.has_warnings else CONFIRM_CONNECTION_VERBIAGE
            prompt_connection(message=prompt, skip_prompt=onboarding_config.connection_options.auto_yes)
            self._add_connection(temp_path=result.credentials_key, onboarding_config=onboarding_config)
        else:
            click.echo(SKIP_ADD_CONNECTION_VERBIAGE)

    def handle_cert(self, cert_prefix: str, options: Dict) -> None:
        """
        Handles cert payload from either an s3 path or file. Uploading the latter
        Options is updated if successful.
        """
        if options.get('cert_file') is not None:
            bucket_name = self._get_dc_property(prop='PrivateS3BucketArn').split(':')[5]  # get name from arn
            object_name = os.path.join(cert_prefix, os.path.basename(options['cert_file']))
            self._aws_wrapper.upload_file(bucket_name=bucket_name, object_name=object_name,
                                          file_path=options['cert_file'])

            click.echo(f"Uploaded '{options['cert_file']}' to s3://{bucket_name}/{object_name}")
            options['cert_s3'] = object_name

        ssl_options = {}
        if options.get('cert_s3') is not None:
            # reformat to generic options and specify a mechanism
            ssl_options = {'mechanism': S3_CERT_MECHANISM, 'cert': options.pop('cert_s3')}
        options.pop('cert_file', None)

        if options.get('skip_cert_verification') is not None:
            ssl_options['skip_verification'] = options.pop('skip_cert_verification')

        if ssl_options:
            options['ssl_options'] = ssl_options

    def _validate_connection(self, query: str, response_field: str, **kwargs) -> ValidationResult:
        """
        Validate connection before adding using the expected gql response_field (e.g. testPrestoCredentials)
        """
        response = self._request_wrapper.make_request_v2(
            query=query,
            operation=response_field,
            variables=kwargs
        )

        summary = self._build_validation_summary(response.data)
        temp_path = response.data.get('key')
        warnings = response.data.get('warnings')

        if temp_path is not None:
            click.echo(f'{CONNECTION_TEST_SUCCESS_VERBIAGE}{summary}')
            return ValidationResult(
                has_warnings=warnings is not None and len(warnings) > 0,
                credentials_key=temp_path
            )

        complain_and_abort(f'{CONNECTION_TEST_FAILED_VERBIAGE}{summary}')

    def _build_validation_summary(self, response: Dict, table_format: Optional[str] = 'fancy_grid') -> str:
        data = []
        if response.get('validations'):
            for passed in response.get('validations'):
                data.append([
                    passed.get('message'),
                    self._VALIDATION_PASSED,
                    None
                ])

        if response.get('warnings'):
            for failed in response.get('warnings', []):
                data.append([
                    failed.get('message'),
                    self._VALIDATION_FAILED,
                    failed.get('data', {}).get('error')
                ])

        if data:
            return '\n' + tabulate(data, headers=self._VALIDATION_STATUS_HEADERS, tablefmt=table_format)

        # do not provide a summary if no detailed response is available
        return ''

    def _add_connection(self, temp_path: str, onboarding_config: OnboardingConfiguration) -> bool:
        """
        Add connection and setup any associated jobs
        """
        warehouse_type = onboarding_config.warehouse_type or DATA_LAKE_WAREHOUSE_TYPE  # default to data-lake
        connection_request = {'key': temp_path, 'connectionType': onboarding_config.connection_type}
        connection_request.update(self._disambiguate_warehouses(warehouse_type))

        # Set optional properties
        if onboarding_config.warehouse_name:
            connection_request['name'] = onboarding_config.warehouse_name
        if onboarding_config.job_types:
            connection_request['jobTypes'] = onboarding_config.job_types
        if onboarding_config.job_limits:
            connection_request['jobLimits'] = json.dumps(onboarding_config.job_limits)
        if onboarding_config.connection_options and onboarding_config.connection_options.dc_id:
            connection_request['dcId'] = onboarding_config.connection_options.dc_id

        response = self._request_wrapper.make_request_v2(
            query=onboarding_config.connection_query or ADD_CONNECTION_MUTATION,
            operation=onboarding_config.connection_response or EXPECTED_ADD_CONNECTION_RESPONSE_FIELD,
            variables=connection_request,
        )
        connection_id = response.data.get('connection', {}).get('uuid')
        if connection_id is not None:
            click.echo(f"{ADD_CONNECTION_SUCCESS_VERBIAGE}"
                       f"{GQL_TO_FRIENDLY_CONNECTION_MAP.get(onboarding_config.connection_type, onboarding_config.connection_type.capitalize())}.")
            return True
        complain_and_abort(ADD_CONNECTION_FAILED_VERBIAGE)

    def _disambiguate_warehouses(self, warehouse_type: str) -> Dict:
        """
        Determine type of connection request to build using the following criteria -
            1) Does an existing warehouse exist and is it a data-lake? If so, attach connection.
            2) Otherwise, it is either the first connection or traditional warehouse (e.g. redshift, snowflake, etc.)

        Multiple lakes are not supported.
        """
        if len(self._user_service.warehouses) > 0 and warehouse_type == DATA_LAKE_WAREHOUSE_TYPE:
            for warehouse in self._user_service.warehouses:
                if normalize_gql(warehouse['connectionType']) == DATA_LAKE_WAREHOUSE_TYPE:
                    return {'dwId': warehouse['uuid']}
        return {'createWarehouseType': warehouse_type}

    def _get_dc_property(self, prop: str) -> Optional[str]:
        """
        Retrieve property from DC stack outputs
        """
        self._dc_outputs = self._dc_outputs or self._aws_wrapper.get_stack_outputs(
            self._user_service.active_collector['stackArn'])  # cache lookup
        for output in self._dc_outputs:
            if output['OutputKey'] == prop:
                return output['OutputValue']

    @staticmethod
    def _build_connection_options(**kwargs) -> ConnectionOptions:
        """
        Create connection options from arguments
        """
        connection_options = ConnectionOptions(**kwargs)

        if connection_options.monolith_connection_payload:
            connection_options.monolith_base_payload['connectionOptions'] = connection_options.monolith_connection_payload
        return connection_options
