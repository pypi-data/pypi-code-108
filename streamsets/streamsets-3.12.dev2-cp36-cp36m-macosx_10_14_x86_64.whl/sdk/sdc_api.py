# Copyright 2021 StreamSets Inc.

"""Abstractions to interact with the SDC REST API."""

import base64
import datetime
import io
import json
import logging
import os
import urllib
import urllib3
import zipfile
from collections import namedtuple
from functools import wraps
from time import sleep, time
from urllib.parse import parse_qs, urlparse

import javaproperties
import requests
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from . import sdc_models
from .constants import ENGINE_AUTHENTICATION_METHOD_ASTER
from .exceptions import BadRequestError, InternalServerError
from .utils import Version, get_params, join_url_parts, pipeline_json_encoder, wait_for_condition

logger = logging.getLogger(__name__)

# Any headers that the SDC requires for all calls should be added to this dictionary.
REQUIRED_HEADERS = {'X-Requested-By': 'sdc',
                    'X-SS-REST-CALL': 'true',
                    'content-type': 'application/json'}

DEFAULT_SDC_API_VERSION = 1

EXPIRATION_EPOCH_MILLIS_PROP = 'expiration.epoch.millis'
EXPIRATION_WARNING_SECONDS = 60 * 60 * 24 * 7  # seconds in a week

PUBLIC_KEY = RSA.import_key("""-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA0zS736JSVr96i1vdrhyE
4rSGBu6Z1aMoWJN5KTEG6VektfubE70bwy+er6E1HAAmzxvf5SPfChIUbfzu6SSq
y/PCq+Z9waJ6XtvpbsNtREUTmuJeKGG3QCdt5jZtsVcZkDS6ECKSBB5MDvR5j2B6
fpyxzxyZDbPC8XzwU23kDDp+kks7gjHP4yq5niBx8bt5uegttrU3+z1jKuwhELaJ
rE7sjaJYhaCL/rSXy+5TYVXDPHbFbaAsUnyrDaGx615r+Pv2Hh3aZ8f3UihXVosa
Q/hsgBue6WyVggXyLOxQkJIO5ucZD3uzGmSaCsy0SqHOcKS6ijE4nWiT4nuw+vxH
4SNM5KOdzHewOEu7hcjixzxyrC4n9IWc+KboM34anigwUEZaXQouiUxP5mMwcxth
4sxj65HV5Fi7Hx63d+NAVefDgsd4SnLIZGEq+8aNCJPNgs8fHcgclcYjLpnoIIVG
Pss+mafT4com2FaPnaUQTHeWd1tdbkj8WthX3klKMCE/V/37sJdfPPWX8jM2nnaj
LRr2RStMuISF4Sdu/jQhM4lIpiRnmH8kRZXFl96xgZjVITDDQ50Mk+Q68MLUs9Zg
fP1NpydErGHV78PDyA6KIStnJdRRG6qzPUbxqhRWafhMRflsaGrFBZi+eg6QloI5
I5BMEDmwZ9fTBRVkzq3AVcECAwEAAQ==
-----END PUBLIC KEY-----""")


class ApiClient(object):
    """
    API client to communicate with an SDC instance.

    Args:
        server_url (:obj:`str`): Complete URL to SDC server.
        aster_authentication_token (:obj:`str`, optional): Aster authentication token. Default: ``None``
        aster_server_url (:obj:`str`, optional): Aster server base URL. Default: ``None``
        authentication_method (:obj:`str`, optional): StreamSets Data Collector authentication method. Default: ``None``
        api_version (:obj:`int`, optional): The API version. Default: :py:const:`sdc_api.DEFAULT_SDC_API_VERSION`
        dump_log_on_error (:obj:`bool`, optional): Print logs when an API error occurs. Default: ``False``
        session_attributes (:obj:`dict`, optional): A dictionary of attributes to set on the underlying
            :py:class:`requests.Session` instance at initialization. Default: ``None``
        headers (:obj:`dict`, optional): A dictionary of headers to with the :py:class:`requests.Session` instance.
            Default: ``None``
    """
    def __init__(self,
                 server_url,
                 aster_authentication_token=None,
                 aster_server_url=None,
                 authentication_method=None,
                 api_version=DEFAULT_SDC_API_VERSION,
                 dump_log_on_error=False,
                 session_attributes=None,
                 headers=None,
                 **kwargs):
        self.server_url = server_url
        self.authentication_method = authentication_method
        self.aster_authentication_token = aster_authentication_token
        self.aster_server_url = aster_server_url

        self.session = requests.Session()

        self.api_version = api_version
        logger.info('Authentication method = %s', self.authentication_method)
        # TODO: Look into if we need the following check for ASTER. JIRA https://issues.streamsets.com/browse/TLKT-718
        # if self.authentication_method == ENGINE_AUTHENTICATION_METHOD_ASTER:
        #    if aster_authentication_token is not None and aster_server_url is not None:
        #        self._register_with_aster_and_login()
        #    else:
        #        raise ValueError('aster_authentication_token and aster_server_url are mandatory parameters')

        self.session.headers.update(REQUIRED_HEADERS)

        if headers:
            self.session.headers.update(headers)
        if session_attributes:
            for attribute, value in session_attributes.items():
                setattr(self.session, attribute, value)
        if not self.session.verify:
            # If we disable SSL cert verification, we should disable warnings about having disabled it.
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.api_version = api_version
        self.dump_log_on_error = dump_log_on_error

        self._tunneling_instance_id = None
        if 'tunneling' in self.server_url:
            logger.debug('Getting tunneling instance id ...')
            result = self._fetch_tunneling_instance_id()
        logger.debug('tunneling_instance_id is %s', self._tunneling_instance_id)
        # We explicitly wait for SDC connectivity to workaround an observed race condition wherein
        # an ControlHub-registered SDC takes several seconds after its port is available before it
        # correctly serves requests on startup.
        logger.debug('Confirming connectivity to Data Collector server ...')

        def sdc_connectivity_established(api_client):
            try:
                api_client.version = api_client.get_sdc_info()['version']
                logger.debug('Connected to SDC v%s', api_client.version)
                return True
            except requests.exceptions.HTTPError as http_error:
                logger.debug('Call to SDC info endpoint failed. Trying again ...')
            except KeyError:
                logger.debug('Invalid SDC info received. Trying again ...')

        wait_for_condition(sdc_connectivity_established, [self])

    def _fetch_tunneling_instance_id(self):
        def _get_tunneling_instance_id(api_client):
            try:
                parsed_uri = urlparse(api_client.server_url)
                sch_url = '{}://{}'.format(parsed_uri.scheme, parsed_uri.netloc)
                end_point = '{}/tunneling/rest/connection/{}'.format(sch_url, parsed_uri.path.split('/tunneling/rest/')[1])
                response = api_client._get(end_point, absolute_endpoint=True)
                if not response:
                    raise Exception('This Engine is not accessible. There is no active WebSocket session to the'
                                    'Tunneling application from this engine. Trying again ...')
                self._tunneling_instance_id = response.json()['instanceId']
                logger.debug('Fetched tunneling_instance_id is %s', self._tunneling_instance_id)
                return self._tunneling_instance_id
            except requests.exceptions.HTTPError as http_error:
                logger.debug('Call to fetch tunneling instance id endpoint failed. Trying again ...')
            except KeyError:
                logger.debug('Invalid tunneling instance id received. Trying again ...')
            except Exception as ex:
                logger.debug(ex)
        wait_for_condition(_get_tunneling_instance_id, [self], timeout=300)

    def get_sdc_info(self):
        """Get SDC info.

        Returns:
            A :obj:`dict` of SDC system info.
        """
        response = self._get(endpoint='/v{0}/system/info'.format(self.api_version))
        return response.json() if response.content else {}

    def get_sdc_directories(self):
        """Get SDC directories.

        Returns:
            A :obj:`dict` of SDC directories.
        """
        response = self._get(endpoint='/v{0}/system/directories'.format(self.api_version))
        return response.json() if response.content else {}

    def get_sdc_configuration(self):
        """Get all SDC configuration.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """
        response = self._get(endpoint='/v{0}/system/configuration'.format(self.api_version))
        return Command(self, response)

    def get_sdc_log_config(self):
        """Get SDC log config.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """
        response = self._get(endpoint='/v{0}/system/log/config'.format(self.api_version))
        return Command(self, response)

    def get_sdc_ui_configuration(self):
        """Get SDC UI configuration.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """
        response = self._get(endpoint='/v{0}/system/configuration/ui'.format(self.api_version))
        return Command(self, response)

    def get_pipeline_committed_offsets(self, pipeline_id, rev=0):
        """Get pipeline committed offsets.

        Args:
            pipeline_id (:obj:`str`)
            rev (:obj:`int`, optional): Default: ``0``

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """
        response = self._get(endpoint='/v{}/pipeline/{}/committedOffsets'.format(self.api_version,
                                                                                 pipeline_id))
        return Command(self, response)

    def update_pipeline_committed_offsets(self, pipeline_id, rev=0, body=None):
        """Update pipeline committed offsets.

        Args:
            pipeline_id (:obj:`str`)
            rev (:obj:`int`, optional): Default: ``0``
            body (:obj:`dict`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self', 'pipeline_id', 'body'))
        response = self._post(endpoint='/v{}/pipeline/{}/committedOffsets'.format(self.api_version,
                                                                                  pipeline_id),
                              params=params,
                              data=body)
        return Command(self, response)

    def validate_pipeline(self, pipeline_id, rev=0, timeout_sec=2000):
        """Validate a pipeline.

        Args:
            pipeline_id (:obj:`str`)
            rev (:obj:`int`, optional): Revision of the pipeline. Default: 0
            timeout_sec (:obj:`int`, optional): Validation timeout, in seconds. Default: 2000

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.ValidateCommand`
        """
        response = self._get(endpoint='/v{}/pipeline/{}/validate'.format(self.api_version, pipeline_id),
                             params={'rev': rev, 'timeout': timeout_sec})
        previewer_id = response.json()['previewerId']
        return ValidateCommand(self, response, pipeline_id, previewer_id)

    def reset_origin_offset(self, pipeline_id, rev=0):
        """Reset origin offset.

        Args:
            pipeline_id (:obj:`str`)
            rev (:obj:`int`, optional): Revision of the pipeline. Default: ``0``

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self',
                                                             'pipeline_id'))
        response = self._post(endpoint='/v{}/pipeline/{}/resetOffset'.format(self.api_version, pipeline_id),
                              params=params)
        return Command(self, response)

    def get_pipeline_configuration(self, pipeline_id, rev=0, get='pipeline'):
        """Get pipeline configuration.

        Args:
            pipeline_id (:obj:`str`)
            rev (:obj:`int`, optional): Revision of the pipeline. Default: 0
            get (:obj:`str`, optional): Default: ``pipeline``

        Returns:
            A :obj:`dict` of pipeline configuration informaton.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'pipeline_id'))
        response = self._get(endpoint='/v{}/pipeline/{}'.format(self.api_version, pipeline_id),
                             params=params)
        return response.json() if response.content else {}

    def update_pipeline_configuration(self, pipeline_id, pipeline_json, rev=0, description=None):
        """Update pipeline configuration.

        Args:
            pipeline_id (:obj:`str`)
            pipeline_json (:obj:`str`): Pipeline in JSON format.
            rev (:obj:`int`, optional): Revision of the pipeline. Default: 0
            description (:obj:`int`, optional): Update description. Default: ``None``

        Returns:
            A :obj:`dict` of response content.
        """
        response = self._post(endpoint='/v{}/pipeline/{}'.format(self.api_version, pipeline_id),
                              params={'rev': rev, 'description': description},
                              data=pipeline_json)
        return response.json() if response.content else {}

    def import_fragment(self, fragment_id, fragment_json, draft=False, include_library_definitions=None):
        """Import a fragment.

        Args:
            fragment_id (:obj:`str`)
            fragment_json (:obj:`str`): Fragment in JSON format.
            draft (:obj:`bool`, optional): If True, fragment will be imported but not added to SDC store.
            include_library_definitions (:obj:`bool`, optional): Default: ``None``.

        Returns:
            A Python object with the JSON response content.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'fragment_id', 'fragment_json'))
        response = self._post(endpoint='/v{}/fragment/{}/import'.format(self.api_version, fragment_id),
                              params=params,
                              data=fragment_json)
        return response.json() if response.content else {}

    def import_pipeline(self, pipeline_id, pipeline_json, rev=0, overwrite=False, draft=False,
                        include_library_definitions=None, auto_generate_pipeline_id=None):
        """Import a pipeline.

        Args:
            pipeline_id (:obj:`str`)
            pipeline_json (:obj:`str`): Pipeline in JSON format.
            rev (:obj:`int`): Revision of the pipeline.
            overwrite (:obj:`bool`): Overwrite the pipeline if it already exists.
            draft (:obj:`bool`, optional): If True, pipeline will be imported but not added to SDC store.
            include_library_definitions (:obj:`bool`, optional): Default: ``None``.
            auto_generate_pipeline_id (:obj:`bool`, optional): If True, pipeline ID will be generated by
                concatenating a UUID to a whitespace-stripped version of the pipeline title. If
                False, the pipeline title will be used as the pipeline ID. Default: ``None``

        Returns:
            A Python object with the JSON response content.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'pipeline_id', 'pipeline_json'))
        response = self._post(endpoint='/v{}/pipeline/{}/import'.format(self.api_version, pipeline_id),
                              params=params,
                              data=pipeline_json)
        return response.json() if response.content else {}

    def import_pipelines(self, pipelines_file):
        """Import pipelines from archived zip directory.

        Args:
            pipelines_file (:obj:`file`): file containing the pipelines

        Returns:
            A Python object with the JSON response content.
        """
        response = self._post(endpoint='/v{}/pipelines/import'.format(self.api_version),
                              files={'file': pipelines_file},
                              headers={'content-type': None})
        return response.json() if response.content else {}

    def export_pipeline(self, pipeline_id, rev=0, attachment=False, include_library_definitions=False,
                        include_plain_text_credentials=True):
        """Export a pipeline.

        Args:
            pipeline_id (:obj:`str`)
            rev (:obj:`int`): Revision of the pipeline. Default ``0``.
            attachment (:obj:`boolean`): Default ``False``.
            include_library_definitions (:obj:`boolean`): Library definitions needed for StreamSets Next.
                                                          Default ``False``.
            include_plain_text_credentials (:obj:`boolean`): Default ``True``.

        Returns:
            A Python object with the JSON response content.
        """

        params = get_params(parameters=locals(), exclusions=('self',
                                                             'pipeline_id'))
        response = self._get(endpoint='/v{0}/pipeline/{1}/export'.format(self.api_version,
                                                                         pipeline_id),
                             params=params)
        return response.json() if response.content else {}

    def export_pipelines(self, body, include_library_definitions=False, include_plain_text_credentials=True):
        """Export pipelines.

        Args:
            body (:obj:`str`)
            include_library_definitions (:obj:`bool`, optional): Default: ``False``.
            include_plain_text_credentials (:obj:`bool`, optional): Default: ``True``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self', 'body'))
        response = self._post(endpoint='/v{}/pipelines/export'.format(self.api_version),
                              params=params,
                              data=body)
        return Command(self, response)

    def update_pipeline(self, pipeline_id, pipeline, rev=0, description=None):
        """Update a pipeline.

        Args:
            pipeline_id (:obj:`str`)
            pipeline (:obj:`str`): Pipeline configuration in JSON format.
            rev (:obj:`int`, optional): Revision of the pipeline. Default: ``0``.
            description (:obj:`str`, optional): Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self', 'pipeline_id', 'pipeline'))
        response = self._post(endpoint='/v{}/pipeline/{}'.format(self.api_version, pipeline_id),
                              params=params,
                              data=pipeline)
        return Command(self, response)

    def get_all_pipeline_configuration_info(self, filter_text=None, label=None, offset=None,
                                            len_=-1, order_by='NAME', order='ASC', include_status=None):
        """Returns all Pipeline Configuration Info.

        Args:
            filter_text (:obj:`str`, optional): Default: ``None``
            label (:obj:`str`, optional): Default: ``None``
            offset (:obj:`int`, optional): Default: ``None``
            len_ (:obj:`int`, optional): Default: ``-1``
            order_by (:obj:`str`, optional): Default: ``'NAME'``
            order (:obj:`str`, optional): Default: ``'ASC'``
            include_status (:obj:`bool`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(endpoint='/v{}/pipelines'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def create_fragment(self, title, description=None, draft=None, execution_mode=None, body=None):
        """Add a new pipeline configuration to the store.
        Args:
            title (:obj:`str`)
            description (:obj:`str`, optional): Default: ``None``
            draft (:obj:`bool`, optional): If True, fragment will be created but not added to SDC store.
                Default: ``None``
            execution_mode (:obj:`str`, optional): Default: `` None``
            body (:obj:`dict`, optional): Default: ``None``
        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self', 'title'))
        response = self._put(endpoint='/v{}/fragment/{}'.format(self.api_version, title),
                             params=params,
                             data=body,
                             is_data_format_json=False)
        return Command(self, response)

    def create_pipeline(self, pipeline_title, description=None,
                        auto_generate_pipeline_id=None, draft=None, pipeline_type="DATA_COLLECTOR"):
        """Add a new pipeline configuration to the store.

        Args:
            pipeline_title (:obj:`str`)
            description (:obj:`str`, optional): Default: ``None``
            auto_generate_pipeline_id (:obj:`bool`, optional): If True, pipeline ID will be generated by
                concatenating a UUID to a whitespace-stripped version of the pipeline title. If
                False, the pipeline title will be used as the pipeline ID. Default: ``None``
            draft (:obj:`bool`, optional): If True, pipeline will be created but not added to SDC store.
                Default: ``None``
            pipeline_type (:obj:`str`, optional): Default: ``DATA_COLLECTOR``

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """
        # Before 2.5.0.0, the autoGeneratePipelineId parameter was called autoGenerateName.
        if Version(self.version) < Version('2.5.0.0'):
            auto_generate_name = auto_generate_pipeline_id
            del auto_generate_pipeline_id

        params = get_params(parameters=locals(), exclusions=('self', 'pipeline_title'))
        response = self._put(endpoint='/v{0}/pipeline/{1}'.format(self.api_version,
                                                                  pipeline_title),
                             params=params)
        return Command(self, response)

    def import_fragment(self, fragment_id, fragment_json, draft=False, include_library_definitions=None):
        """Import a fragment.

        Args:
            fragment_id (:obj:`str`)
            fragment_json (:obj:`str`): Fragment in JSON format.
            draft (:obj:`bool`, optional): If True, fragment will be imported but not added to SDC store.
                Default: ``False``.
            include_library_definitions (:obj:`bool`, optional): Default: ``None``.

        Returns:
            A Python object with the JSON response content.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'fragment_id', 'fragment_json'))
        response = self._post(endpoint='/v{}/fragment/{}/import'.format(self.api_version, fragment_id),
                              params=params,
                              data=fragment_json)
        return response.json() if response.content else {}

    def delete_pipeline(self, pipeline_id):
        """Delete a pipeline configuration.

        Args:
            pipeline_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """

        response = self._delete(endpoint='/v{0}/pipeline/{1}'.format(self.api_version,
                                                                     pipeline_id))
        return Command(self, response)

    def start_pipeline(self, pipeline_id, rev=0, runtime_parameters=None):
        """Start a pipeline.

        Args:
            pipeline_id (:obj:`str`): Pipeline ID.
            rev (:obj:`int`): Revision of the pipeline.
            runtime_parameters (:obj:`dict`): Runtime Parameters to override Pipeline Parameters value.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.StartPipelineCommand`
        """
        response = self._post(endpoint='/v{}/pipeline/{}/start'.format(self.api_version,
                                                                       pipeline_id),
                              params={'rev': rev}, data=runtime_parameters)
        return StartPipelineCommand(self, response)

    def get_pipeline_status(self, pipeline_id, rev=0, only_if_exists=None):
        """Get status of a pipeline.

        Args:
            pipeline_id (:obj:`str`)
            rev (:obj:`int`, optional): Revision of the pipeline. Default: ``0``
            only_if_exists (:obj:`bool`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.PipelineCommand`
        """
        params = get_params(parameters=locals(), exclusions=('self', 'pipeline_id'))
        response = self._get(endpoint='/v{}/pipeline/{}/status'.format(self.api_version,
                                                                       pipeline_id),
                             params=params)
        return PipelineCommand(self, response)

    def get_pipeline_rules(self, pipeline_id, rev=0):
        """Get pipeline rules.

        Args:
            pipeline_id (:obj:`str`)
            rev (:obj:`int`, optional): Revision of the pipeline. Default: ``0``

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self', 'pipeline_id'))
        response = self._get(endpoint='/v{}/pipeline/{}/rules'.format(self.api_version,
                                                                      pipeline_id),
                             params=params)
        return Command(self, response)

    def update_pipeline_rules(self, pipeline_id, pipeline, rev=0):
        """Update a pipeline.

        Args:
            pipeline_id (:obj:`str`)
            pipeline (:obj:`str`): Pipeline rules configuration in JSON format.
            rev (:obj:`int`, optional): Revision of the pipeline. Default: ``0``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self', 'pipeline_id', 'pipeline'))
        response = self._post(endpoint='/v{}/pipeline/{}/rules'.format(self.api_version, pipeline_id),
                              params=params,
                              data=pipeline)
        return Command(self, response)

    def get_pipeline_metrics(self, pipeline_id, rev=0):
        """Get pipeline metrics.

        Args:
            pipeline_id (:obj:`str`)
            rev (:obj:`int`, optional): Revision of the pipeline. Default: ``0``

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`.
        """
        response = self._get(endpoint='/v{0}/pipeline/{1}/metrics'.format(self.api_version,
                                                                          pipeline_id),
                             params={'rev': rev})
        return Command(self, response)

    def get_pipeline_history(self, pipeline_id, rev=0):
        """Get pipeline history.

        Args:
            pipeline_id (:obj:`str`)
            rev (int): Revision of the pipeline.

        Returns:
            The JSON response from the pipeline history endpoint.
        """
        response = self._get(endpoint='/v{0}/pipeline/{1}/history'.format(self.api_version,
                                                                          pipeline_id),
                             params={'rev': rev})
        return response.json() if response.content else []

    def get_pipeline_error_messages(self, pipeline_id, stage_instance_name, rev=0, size=10, edge=False):
        """Get pipeline error messages.

        Args:
            pipeline_id (:obj:`str`): Pipeline ID.
            stage_instance_name (:obj:`str`): Stage instance name.
            rev (:obj:`int`, optional): Default: ``0``
            size (:obj:`int`, optional): Default: ``10``
            edge (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'pipeline_id'))
        response = self._get(endpoint='/v{0}/pipeline/{1}/errorMessages'.format(self.api_version,
                                                                                pipeline_id),
                             params=params)
        return Command(self, response)

    def _register_with_aster_and_login(self):
        """Register the SDC with Aster. Here activation also happens with registration.
        Also perform login as it retuns a cookie that needs to be set for any further communication with SDC.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`.
        """
        response = self._get(self.server_url, absolute_endpoint=True)
        # If not registered already, then do register
        if 'aregistration.html' in response.url:
            lstate_value = parse_qs(urlparse(response.url).query)['lstate'][0]
            # Obtain the information to start a registration using the lstate query string parameter
            # from the previous response
            response = self._get(endpoint='/v{}/aregistration'.format(self.api_version),
                                 params={'lstate': lstate_value})
            # Make POST to the authorizeUri URL to initiate the registration,
            json_data = response.json()['parameters']
            data = urllib.parse.urlencode(json_data)
            headers = {'Authorization': 'Bearer {}'.format(self.aster_authentication_token),
                       'Content-Type': 'application/x-www-form-urlencoded'}
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = self._post(endpoint='{}/api/security/oauth/authorize'.format(self.aster_server_url),
                                  absolute_endpoint=True, headers=headers, data=data, is_data_format_json=False)
            # Make a POST call to the SDC using the query string from the previous response.
            parameters = parse_qs(urlparse(response.url).query)
            # At this point parameters are of the form {'code': ['FvJi3a'], 'state': ['TZlddl']}
            # The following will convert it into the form {'code': 'FvJi3a', 'state': 'TZlddl'}
            params = {key: value[0] for key, value in parameters.items()}
            response = self._post(endpoint='/v{}/aregistration'.format(self.api_version),
                                  params=params)
            assert response.status_code in (200, 302)
            logger.info('Registered SDC with Aster')

        # Start login sequence
        # Obtain the information to start a registration using the lstate query string parameter
        # from the previous response
        lstate_value = parse_qs(urlparse(response.url).query)['lstate'][0]
        response = self._get(endpoint='/v{}/alogin'.format(self.api_version),
                             params={'lstate': lstate_value})
        # Make POST to the authorizeUri URL to initiate the registration,
        # it must be a FORM request (x-www-form-urlencoded)
        json_data = response.json()['parameters']
        data = urllib.parse.urlencode(json_data)
        headers = {'Authorization': 'Bearer {}'.format(self.aster_authentication_token),
                   'Content-Type': 'application/x-www-form-urlencoded'}
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = self._post(endpoint='{}/api/security/oauth/authorize'.format(self.aster_server_url),
                              absolute_endpoint=True, headers=headers, data=data, is_data_format_json=False)
        # Make a POST call to the SDC using the query string from the previous response
        parameters = parse_qs(urlparse(response.url).query)
        # At this point parameters are of the form {'code': ['FvJi3a'], 'state': ['TZlddl']}
        # The following will convert it into the form {'code': 'FvJi3a', 'state': 'TZlddl'}
        params = {key: value[0] for key, value in parameters.items()}
        response = self._post(endpoint='/v{}/alogin'.format(self.api_version),
                              params=params)
        assert response.status_code in (200, 302)
        logger.info('SDC login complete with Aster')

    def get_activation(self):
        """Get activation.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`.
        """
        response = self._get(endpoint='/v{0}/activation'.format(self.api_version))
        return Command(self, response)

    def register(self, activation_endpoint, data):
        """Register the SDC. Here the activation key is sent to the email specified in data.

        Args:
            activation_endpoint (:obj:`str`) The endpoint where to register SDC.
            data (:obj:`dict`): Data to be sent along with the post request.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`.
        """
        response = self._post(endpoint=activation_endpoint, absolute_endpoint=True, data=data)
        return Command(self, response)

    def activate(self, activation_key):
        """Activate SDC using the passed activation key.

        Args:
            activation_key (:obj:`str`) The activation key.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`.
        """
        response = self._post(endpoint='/v{}/activation'.format(self.api_version),
                              data=activation_key,
                              is_data_format_json=False,
                              headers={'content-type': 'text/plain'})
        return Command(self, response)

    def get_sdc_id(self):
        """
        Get SDC ID for the datacollector.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`.
        """
        response = self._get(endpoint='/v{0}/system/info/id'.format(self.api_version))
        return Command(self, response)

    def opt_for_system_stats(self, opt):
        """
        Opt In/Out for Statistics.

        Args:
            opt (:obj:`str`, optional): extra_message, Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`.
        """
        response = self._post(endpoint='/v{0}/system/stats'.format(self.api_version),
                              params={'active': opt})
        return Command(self, response)

    def get_system_stats(self):
        """
        Get system Statistics.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`.
        """
        response = self._get(endpoint='/v{0}/system/stats'.format(self.api_version))
        return Command(self, response)

    def get_jmx_metrics(self):
        """Get SDC JMX metrics.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`.
        """
        response = self._get(endpoint='/v{}/system/jmx'.format(self.api_version))
        return Command(self, response)

    def get_current_user(self):
        """
        Get currently logged-in user and its groups and roles.

        Returns:
            The JSON response containing information about the current user.
        """
        response = self._get(endpoint='/v{0}/system/info/currentUser'.format(self.api_version))
        return response.json() if response.content else {}

    def change_password(self, data_json):
        """Change password for the current user.

        Args:
            data_json (:obj:`str`): Change password data in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`.
        """
        current_user = self.get_current_user()
        endpoint = '/v{}/usermanagement/users/{}/changePassword'
        response = self._post(endpoint=endpoint.format(self.api_version, current_user['user']),
                              data=data_json)
        return Command(self, response)

    def get_logs(self, ending_offset=-1, extra_message=None, pipeline=None, severity=None):
        """Get SDC logs.

        Args:
            ending_offset (:obj:`int`, optional): ending_offset, Default: ``-1``.
            extra_message (:obj:`str`, optional): extra_message, Default: ``None``.
            pipeline (:py:class:`streamsets.sdk.sdc_models.Pipeline`, optional): The pipeline instance,
                                                                                 Default: ``None``.
            severity (:obj:`str`, optional): severity, Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(endpoint='/v{0}/system/logs'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def stop_pipeline(self, pipeline_id, rev=0):
        """Stop a pipeline.

        Args:
            pipeline_id (:obj:`str`)
            rev (:obj:`int`, optional): Revision of the pipeline. Default: ``0``

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.StopPipelineCommand`
        """
        response = self._post(endpoint='/v{}/pipeline/{}/stop'.format(self.api_version,
                                                                      pipeline_id),
                              params={'rev': rev})
        return StopPipelineCommand(self, response)

    def force_stop_pipeline(self, pipeline_id, rev=0):
        """Force stop a pipeline.

        Args:
            pipeline_id (:obj:`str`)
            rev (:obj:`int`, optional): Revision of the pipeline. Default: ``0``

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.StopPipelineCommand`
        """
        response = self._post(endpoint='/v{}/pipeline/{}/forceStop'.format(self.api_version,
                                                                           pipeline_id),
                              params={'rev': rev})
        return StopPipelineCommand(self, response)

    def get_definitions(self):
        """Get SDC definitions.

        Returns:
            A :obj:`list` of stage definition :obj:`dict` instances.
        """
        response = self._get(endpoint='/v{0}/definitions'.format(self.api_version))
        return response.json()

    def get_connection_definitions(self):
        """Get connection definitions.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`.
        """
        response = self._get(endpoint='/v{0}/definitions/connections'.format(self.api_version))
        return Command(self, response)

    def get_snapshots(self):
        """Get information about stored snapshots.

        Returns:
            The JSON response from the pipeline snapshots endpoint.
        """
        response = self._get(endpoint='/v{0}/pipelines/snapshots'.format(self.api_version))
        return response.json() if response.content else []

    def get_snapshots_by_pipeline(self, pipeline_id):
        """Get information about stored snapshots.

        Args:
            pipeline_id (:obj:`str`): The ID of the pipeline to retrieve snapshots for.

        Returns:
            The JSON response from the pipeline snapshots endpoint.
        """
        response = self._get(endpoint='/v{}/pipeline/{}/snapshots'.format(self.api_version, pipeline_id))
        return Command(self, response)

    def capture_snapshot(self, pipeline_id, snapshot_name, snapshot_label, rev=0,
                         batches=1, batch_size=10, start_pipeline=False,
                         runtime_parameters=None):
        """Capture a snapshot.
        Args:
            pipeline_id (:obj:`str`)
            snapshot_name (:obj:`str`): Name of the snapshot.
            snapshot_label (:obj:`str`)
            rev (:obj:`int`, optional). Default: ``0``
            runtime_parameters (:obj:, optional)
        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.SnapshotCommand`
        """
        params = get_params(parameters=locals(), exclusions=('self',
                                                             'pipeline_id',
                                                             'snapshot_name'))
        response = self._put(endpoint='/v{}/pipeline/{}/snapshot/{}'.format(self.api_version,
                                                                            pipeline_id,
                                                                            snapshot_name),
                             params=params, data=runtime_parameters)
        return SnapshotCommand(self, response, pipeline_id, snapshot_name, snapshot_label)

    def get_snapshot_status(self, pipeline_id, snapshot_name, rev=0):
        """Get the status of a snapshot.

        Args:
            pipeline_id (:obj:`str`)
            snapshot_name (:obj:`str`): Name of the snapshot.
            rev (:obj:`int`, optional). Default: ``0``

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self',
                                                             'pipeline_id',
                                                             'snapshot_name'))
        response = self._get(
            endpoint='/v{}/pipeline/{}/snapshot/{}/status'.format(self.api_version,
                                                                  pipeline_id,
                                                                  snapshot_name),
            params=params
        )
        return Command(self, response)

    def get_snapshot_data(self, pipeline_id, snapshot_name, snapshot_label, rev=0):
        """Get snapshot data.

        Args:
            pipeline_id (:obj:`str`)
            snapshot_name (:obj:`str`): Name of the snapshot.
            snapshot_label (:obj:`str`): Label of the snapshot.
            rev (:obj:`int`, optional). Default: ``0``

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.SnapshotCommand`
        """
        params = get_params(parameters=locals(), exclusions=('self',
                                                             'pipeline_id',
                                                             'snapshot_name'))
        response = self._get(endpoint='/v{}/pipeline/{}/snapshot/{}'.format(self.api_version,
                                                                            pipeline_id,
                                                                            snapshot_name),
                             params=params)
        return SnapshotCommand(self,
                               response,
                               pipeline_id,
                               snapshot_name,
                               snapshot_label)

    def delete_snapshot(self, pipeline_id, snapshot_id, rev=0):
        """Delete a snapshot for a given pipeline.

        Args:
            pipeline_id (:obj:`str`)
            snapshot_id (:obj:`str`): ID of the snapshot.
            rev (:obj:`int`, optional). Default: ``0``
        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self', 'pipeline_id', 'snapshot_id'))
        response = self._delete(endpoint='/v{}/pipeline/{}/snapshot/{}'.format(self.api_version, pipeline_id,
                                                                               snapshot_id))
        return Command(self, response)


    def run_pipeline_preview(self, pipeline_id, rev=0,
                             batches=1, batch_size=10, skip_targets=True,
                             end_stage=None, timeout=2000, test_origin=False,
                             stage_outputs_to_override_json=None):
        """Run pipeline preview.
        Args:
            pipeline_id (:obj:`str`)
            rev (:obj:`int`, optional)
            batches (:obj:`int`, optional)
            batch_size (:obj:`int`, optional)
            skip_targets (:obj:`bool`, optional)
            end_stage (:obj:`str`, optional)
            timeout (:obj:`int`, optional)
            test_origin (:obj:`bool`, optional): Test origin. Default: ``False``
            stage_outputs_to_override_json (:obj:`str`, optional)
        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.PreviewCommand`
        """
        params = get_params(parameters=locals(), exclusions=('self',
                                                             'pipeline_id'))
        response = self._post(endpoint='/v{}/pipeline/{}/preview'.format(self.api_version,
                                                                         pipeline_id),
                              params=params)
        previewer_id = response.json()['previewerId']
        return PreviewCommand(self, response, pipeline_id, previewer_id)

    def get_preview_status(self, pipeline_id, previewer_id):
        """Get the status of a preview.
        Args:
            pipeline_id (:obj:`str`)
            previewer_id (:obj:`int`): Id of the preview.
        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """
        response = self._get(
            endpoint='/v{}/pipeline/{}/preview/{}/status'.format(self.api_version,
                                                                 pipeline_id,
                                                                 previewer_id)
        )
        return Command(self, response)

    def get_preview_data(self, pipeline_id, previewer_id):
        """Get preview data.

        Args:
            pipeline_id (:obj:`str`)
            previewer_id (:obj:`str`): Id of the preview.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.PreviewCommand`
        """
        response = self._get(endpoint='/v{}/pipeline/{}/preview/{}'.format(self.api_version,
                                                                           pipeline_id,
                                                                           previewer_id))
        return PreviewCommand(self, response, pipeline_id, previewer_id)

    def run_dynamic_pipeline_preview(self, preview_json):
        """Run dynamic pipeline preview.

        Args:
            preview_json (:obj:`str`): Preview request in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.PreviewCommand`
        """
        response = self._post(endpoint='/v{0}/pipeline/dynamicPreview'.format(self.api_version), data=preview_json)
        previewer_id = response.json()['previewerId']
        pipeline_id = response.json()['pipelineId']
        return PreviewCommand(self, response, pipeline_id, previewer_id)

    def run_dynamic_pipeline_preview_for_connection(self, preview_json):
        """Run dynamic pipeline preview.
        Args:
            preview_json (:obj:`str`): Preview request in JSON format.
        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.PreviewCommand`
        """
        response = self._post(endpoint='/v{0}/pipeline/dynamicPreview'.format(self.api_version), data=preview_json)
        previewer_id = response.json()['previewerId']
        pipeline_id = response.json()['pipelineId']
        return ConnectionValidateCommand(self, response, pipeline_id, previewer_id)

    def get_stage_libraries_list(self, repo_url, installed_only):
        """Get stage libraries list.
        Args:
            repo_url (:obj:`str`): repo url
            installed_only (:obj:`boolean`): installed only libraries

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(endpoint='/v{}/stageLibraries/list'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_classpath_health(self):
        """Retrieve analysis of each stage library's classpath health."""
        response = self._get(endpoint='/v{}/stageLibraries/classpathHealth'.format(self.api_version))
        return response.json() if response.content else []

    def get_alerts(self):
        """Get pipeline alerts."""
        response = self._get(endpoint='/v{}/pipelines/alerts'.format(self.api_version))
        return response.json() if response.content else []

    def get_bundle_generators(self):
        """Get available support bundle generators."""
        response = self._get(endpoint='/v{}/system/bundle/list'.format(self.api_version))
        return response.json() if response.content else []

    def get_health_categories(self):
        """Get list of available health categories."""
        response = self._get(endpoint='/v{}/system/health/categories'.format(self.api_version))
        return Command(self, response)

    def get_health_report(self, categories=None):
        """Get Health Report for given categories (or all by default)."""
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(endpoint='/v{}/system/health/report'.format(self.api_version), params=params)
        return Command(self, response)

    def get_bundle(self, generators=None):
        """Generate new Support bundle."""
        response = self._get(endpoint='/v{}/system/bundle/generate'.format(self.api_version),
                             params={'generators': ','.join(generators or [])})
        return zipfile.ZipFile(file=io.BytesIO(response.content), mode='r')

    # ACL-related API
    def get_acl_subjects(self):
        """Get all subjects in pipeline ACL.

        Returns:
            A dictionary of subjects in a pipeline ACL.
        """
        response = self._get(endpoint='/v{}/pipelines/subjects'.format(self.api_version))
        return response.json() if response.content else {}

    def set_acl_subjects(self, subjects_json):
        """Update subjects in pipeline ACL.

        Args:
            subjects_json (:obj:`str`): Subjects ACL in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """
        response = self._post(endpoint='/v{0}/pipeline/subjects'.format(self.api_version), data=subjects_json)
        return Command(self, response)

    def get_pipeline_acl(self, pipeline_id):
        """Get pipeline ACL.

        Args:
            pipeline_id (:obj:`str`)

        Returns:
            A JSON representation of the pipeline ACL.
        """
        response = self._get(endpoint='/v{}/acl/{}'.format(self.api_version, pipeline_id))
        return response.json() if response.content else {}

    def set_pipeline_acl(self, pipeline_id, pipeline_acl_json):
        """Update pipeline ACL.

        Args:
            pipeline_id (:obj:`str`)
            pipeline_acl_json (:obj:`str`): Pipeline ACL in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`
        """
        response = self._post(endpoint='/v{}/acl/{}'.format(self.api_version,
                                                            pipeline_id), data=pipeline_acl_json)
        return Command(self, response)

    def get_pipeline_permissions(self, pipeline_id):
        """Return pipeline permissions for given pipeline ID.

        Args:
            pipeline_id (:obj:`str`)

        Returns:
            A list of pipeline permissions.
        """
        response = self._get(endpoint='/v{}/acl/{}/permissions'.format(self.api_version, pipeline_id))
        return response.json() if response.content else []

    # Internal functions only below.
    def _delete(self, endpoint, params={}):
        url = join_url_parts(self.server_url, '/rest', endpoint)
        if self._tunneling_instance_id:
            params.update({'TUNNELING_INSTANCE_ID': self._tunneling_instance_id})
        response = self.session.delete(url, params=params)
        response.raise_for_status()
        return response

    def _get(self, endpoint, params={}, absolute_endpoint=False):
        url = endpoint if absolute_endpoint else join_url_parts(self.server_url, '/rest', endpoint)
        if self._tunneling_instance_id:
            params.update({'TUNNELING_INSTANCE_ID': self._tunneling_instance_id})
        response = self.session.get(url, params=params)
        self._handle_http_error(response)
        return response

    def _post(self, endpoint, absolute_endpoint=False, params={}, data=None, files=None,
              headers=None, is_data_format_json=True):
        url = endpoint if absolute_endpoint else join_url_parts(self.server_url, '/rest', endpoint)
        if is_data_format_json:
            # When we serialize to JSON, we define a default to enable handling of objects (e.g.
            # :py:class:`streamsets.sdk.models.Configuration` embedded in the data).
            data = json.dumps(data, default=pipeline_json_encoder) if data else None
        if self._tunneling_instance_id:
            params.update({'TUNNELING_INSTANCE_ID': self._tunneling_instance_id})
        response = self.session.post(url, params=params, data=data, files=files, headers=headers)
        self._handle_http_error(response)
        return response

    def _put(self, endpoint, params={}, data=None, is_data_format_json=True):
        url = join_url_parts(self.server_url, '/rest', endpoint)
        if is_data_format_json:
            data = json.dumps(data) if data else None
        if self._tunneling_instance_id:
            params.update({'TUNNELING_INSTANCE_ID': self._tunneling_instance_id})
        response = self.session.put(url, params=params, data=data)
        self._handle_http_error(response)
        return response

    def _handle_http_error(self, response):
        """Specific error handling for SDC, to make better error reporting where applicable."""
        if response.status_code == 500:
            raise InternalServerError(response)
        elif response.status_code == 400:
            raise BadRequestError(response)

        # Delegating to response object error handling as last resort.
        response.raise_for_status()


class Command:
    """Command to allow users to interact with commands submitted through SDC REST API.

    Args:
        api_client (:py:class:`streamsets.sdk.sdc_api.ApiClient`): SDC API client.
        response (:py:class:`requests.Response`): Command reponse.
    """
    def __init__(self, api_client, response):
        self.api_client = api_client
        self.response = response

    def dump_sdc_log_on_error(*dec_args, **dec_kwargs):  # pylint: disable=no-method-argument
        """A Python Decorator to log SDC when errors happen.
        Args:
            *dec_args (:obj:, optional): Optional non key-worded arguments to be passed.
            **dec_kwargs (:obj:, optional): Optional key-worded arguments to be passed, such as `all`. `all` will
                log complete SDC.
        """
        def outer_func(func):
            @wraps(func)
            def wrapped(self, *args, **kwargs):
                log_time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')
                try:
                    return func(self, *args, **kwargs)
                except Exception:
                    if self.api_client.dump_log_on_error:
                        get_logs_response = self.api_client.get_logs().response
                        sdc_log_obj = sdc_models.Log(get_logs_response.json() if get_logs_response.content else [])
                        sdc_log = (sdc_log_obj if dec_kwargs.get('all') else sdc_log_obj.after_time(log_time_now))
                        if sdc_log:
                            logger.error('Error during `%s` call. SDC log follows ...', func.__name__)
                            print('------------------------- SDC log - Begins -----------------------')
                            print(sdc_log)
                            print('------------------------- SDC log - Ends -------------------------')
                    raise
            return wrapped

        if len(dec_args) == 1 and not dec_kwargs and callable(dec_args[0]):  # called without args
            return outer_func(dec_args[0])
        else:
            return outer_func


class StatusError(Exception):
    """Parent class for pipeline status errors."""
    def __init__(self, response):
        self.response = response
        self.message = self.response['message']
        super().__init__(self.message)


class StartError(StatusError):
    """Pipeline start error."""
    pass


class StartingError(StatusError):
    """Pipeline starting error."""
    pass


class RunningError(StatusError):
    """Pipeline running error."""
    pass


class RunError(StatusError):
    """Pipeline run error."""
    pass


class ConnectError(StatusError):
    """Pipeline connect error."""
    pass


class PipelineCommand(Command):
    """Pipeline Command to allow users to interact with commands submitted through SDC REST API.

    Args:
        api_client (:py:class:`streamsets.sdk.sdc_api.ApiClient`): SDC API client.
        response (:py:class:`requests.Response`): Command reponse.
    """
    # A simple mapping between error statuses from the SDC API and exceptions to raise.
    ERROR_STATUSES = {
        'START_ERROR': StartError,
        'RUNNING_ERROR': RunningError,
        'RUN_ERROR': RunError,
        'CONNECT_ERROR': ConnectError
    }

    @Command.dump_sdc_log_on_error
    def wait_for_status(self, status, ignore_errors=False, timeout_sec=300):
        """Wait for pipeline status.
        Args:
            status (:obj:`str`): Pipeline status.
            ignore_errors(:obj:`boolean`): If set to true then this method will not throw
                exception if an error state is detected. Particularly useful if the caller
                needs to wait on one of the terminal error states.
            timeout_sec (:obj:`int`): Timeout for wait, in seconds. Default: 300
        """
        logger.info('Waiting for status %s ...', status)
        start_waiting_time = time()
        stop_waiting_time = start_waiting_time + timeout_sec

        while time() < stop_waiting_time:
            try:
                pipeline_id = self.response.json()['pipelineId']
            except KeyError:
                pipeline_id = self.response.json()['name']

            current_status = self.response.json()['status']
            logger.debug('Status of pipeline %s is %s ...', pipeline_id, current_status)

            if (isinstance(status, list) and current_status in status) or current_status == status:
                logger.info('Pipeline %s reached status %s (took %.2f s).',
                            pipeline_id,
                            current_status,
                            time() - start_waiting_time)
                break
            elif not ignore_errors and current_status in PipelineCommand.ERROR_STATUSES:
                raise PipelineCommand.ERROR_STATUSES.get(current_status)(self.response.json())
            else:
                sleep(1)
                self.response = self.api_client.get_pipeline_status(pipeline_id).response
        else:
            raise Exception('Timed out after %s seconds while waiting for status %s.',
                            timeout_sec,
                            status)


class SnapshotCommand(Command):
    """Command returned by snapshot operations.
    Args:
        api_client (:obj:`ApiClient`): SDC API client.
        response (:obj:`requests.Response`): Command response.
        pipeline_id (:obj:`str`)
        snapshot_name (:obj:`str`): Snapshot name.
        snapshot_label (:obj:`str`): Snapshot label.
    """
    def __init__(self, api_client, response, pipeline_id, snapshot_name, snapshot_label):
        super().__init__(api_client=api_client, response=response)
        self.pipeline_id = pipeline_id
        self.snapshot_name = snapshot_name
        self.snapshot_label = snapshot_label

    @property
    @Command.dump_sdc_log_on_error
    def snapshot(self):
        """The Snapshot object returned by this snapshot command.
        Returns:
            (:obj:`sdc_models.Snapshot`)
        """
        snapshot = self.api_client.get_snapshot_status(pipeline_id=self.pipeline_id,
                                                            snapshot_name=self.snapshot_name).response.json()
        snapshot.update(self.api_client.get_snapshot_data(pipeline_id=self.pipeline_id,
                                                               snapshot_name=self.snapshot_name,
                                                               snapshot_label=self.snapshot_label).response.json())
        return sdc_models.Snapshot(api_client=self.api_client,
                                   snapshot=snapshot)

    @Command.dump_sdc_log_on_error
    def wait_for_finished(self, timeout_sec=30):
        """Wait for snapshot to complete."""

        logger.info('Waiting for snapshot to be captured...')
        start_waiting_time = time()
        stop_waiting_time = start_waiting_time + timeout_sec

        while time() < stop_waiting_time:
            self.response = self.api_client.get_snapshot_status(
                pipeline_id=self.pipeline_id,
                snapshot_name=self.snapshot_name
            ).response
            logger.debug('response.content: %s',
                         self.response.content)
            # Loop back until response content starts coming through.
            if not self.response.content:
                continue

            current_status = self.response.json()['inProgress']
            logger.debug('Pipeline (%s) snapshot (%s) in progress: %s',
                         self.pipeline_id,
                         self.snapshot_name,
                         current_status)

            if current_status is False:
                logger.info('Pipeline (%s) snapshot (%s) complete (took %.2f s).',
                            self.pipeline_id,
                            self.snapshot_name,
                            time() - start_waiting_time)
                return self
            sleep(1)

        # We got out of the loop and did not get to the finished state.
        raise TimeoutError('Timed out after {} seconds while '
                           'waiting for status FINISHED.'.format(timeout_sec))


class StartPipelineCommand(PipelineCommand):
    """Pipeline start command to allow users to interact with commands submitted
    through SDC REST API.

    Args:
        api_client (:py:class:`streamsets.sdk.sdc_api.ApiClient`): SDC API client.
        response (:py:class:`requests.Response`): Command reponse.
    """
    def wait_for_finished(self, timeout_sec=300):
        """
        Wait for pipeline to be finished.
        Args:
            timeout_sec (int): Timeout for wait, in seconds. Default: 300
        """
        self.wait_for_status(status='FINISHED', timeout_sec=timeout_sec)

    def wait_for_pipeline_error_records_count(self, count, timeout_sec=300):
        """Wait for pipeline until error records count is reached.
        Args:
            count (:obj:`int`): Record count.
            timeout_sec (:obj:`int`): Timeout for wait, in seconds. Default: 300
        """
        self.wait_for_counters_metric('pipeline.batchErrorRecords.counter', count, timeout_sec)

    def wait_for_pipeline_output_records_count(self, count, timeout_sec=300):
        """Wait for pipeline until output records count is reached.
        Args:
            count (:obj:`int`): Record count.
            timeout_sec (:obj:`int`): Timeout for wait, in seconds. Default: 300
        """
        self.wait_for_counters_metric('pipeline.batchOutputRecords.counter', count, timeout_sec)

    def wait_for_pipeline_batch_count(self, count, timeout_sec=300):
        """Wait for pipeline until batch count is reached.
        Args:
            count (:obj:`int`): Batch count.
            timeout_sec (:obj:`int`): Timeout for wait, in seconds. Default: 300
        """
        self.wait_for_counters_metric('pipeline.batchCount.counter', count, timeout_sec)

    # TODO: Come up with cleaner way to wait for various metrics.
    @Command.dump_sdc_log_on_error
    def wait_for_counters_metric(self, metric_name, target_count, timeout_sec=300):
        """Wait for pipeline till 'counters' count metric.

        Args:
            counters_metric (int): count of 'counters' metric.
            timeout_sec (int): Timeout for wait, in seconds. Default: 300
        """
        try:
            pipeline_id = self.response.json()['pipelineId']
        except KeyError:
            pipeline_id = self.response.json()['name']

        logger.info('Waiting for counters metric %s to reach at least %s...',
                    metric_name,
                    target_count)
        start_waiting_time = time()
        stop_waiting_time = start_waiting_time + timeout_sec

        while time() < stop_waiting_time:
            current_status = self.response.json()['status']
            if current_status in PipelineCommand.ERROR_STATUSES:
                raise PipelineCommand.ERROR_STATUSES.get(current_status)(self.response.json())

            current_counters_metrics = self.api_client.get_pipeline_metrics(
                pipeline_id=pipeline_id
            ).response.json().get('counters', {})

            if current_counters_metrics.get(metric_name, {'count': -1})['count'] >= target_count:
                logger.info('Pipeline %s reached counters metric %s of value %s (took %.2f s).',
                            pipeline_id,
                            metric_name,
                            current_counters_metrics[metric_name]['count'],
                            time() - start_waiting_time)
                break

            sleep(1)
            self.response = self.api_client.get_pipeline_status(
                pipeline_id=pipeline_id
            ).response

        else:
            # We got out of the loop and did not get the metric we were waiting for
            raise TimeoutError('Did not reached metric {} of value {}'.format(metric_name, target_count))


class StopPipelineCommand(PipelineCommand):
    """
    Pipeline stop command to allow users to interact with commands submitted
    through SDC REST API.

    Args:
        api_client (:py:class:`streamsets.sdk.sdc_api.ApiClient`): SDC API client.
        response (:py:class:`requests.Response`): Command reponse.
    """
    def wait_for_stopped(self, timeout_sec=300):
        """
        Wait for pipeline to be stopped.
        Args:
            timeout_sec (int): Timeout for wait, in seconds. Default: 300
        """
        self.wait_for_status(status='STOPPED', timeout_sec=timeout_sec)


class ValidateCommand(Command):
    """Command returned by validate operations.
    Args:
        api_client (:obj:`ApiClient`): SDC API client.
        response (:obj:`requests.Response`): Command response.
        pipeline_id (:obj:`str`)
        previewer_id (:obj:`str`): Previewer_id.
    """
    def __init__(self, api_client, response, pipeline_id, previewer_id):
        super().__init__(api_client=api_client, response=response)
        self.pipeline_id = pipeline_id
        self.previewer_id = previewer_id

    @Command.dump_sdc_log_on_error
    def wait_for_validate(self, timeout_sec=60):
        """Wait for validate to be finished.

        Args:
            timeout_sec (:obj:`int`, optional): Timeout for wait, in seconds. Default: 60
        """
        logger.info('Waiting for validate to be finished ...')
        start_waiting_time = time()
        stop_waiting_time = start_waiting_time + timeout_sec

        while time() < stop_waiting_time:
            self.response = self.api_client.get_preview_status(
                pipeline_id=self.pipeline_id,
                previewer_id=self.previewer_id
            ).response
            logger.debug('response.content: %s', self.response.content)
            # Loop back until response content starts coming through.
            if not self.response.content:
                continue

            current_status = self.response.json()['status']
            if current_status != 'VALIDATING':
                if current_status != 'VALID':
                    preview = self.api_client.get_preview_data(pipeline_id=self.pipeline_id,
                                                               previewer_id=self.previewer_id)
                    self.response = preview.response

                logger.debug('Pipeline (%s) preview (%s) reached state : %s',
                             self.pipeline_id,
                             self.previewer_id,
                             current_status)
                return self

            sleep(1)

        raise Exception('Timed out after %s seconds while waiting for validation.', timeout_sec)


class PreviewCommand(Command):
    """Command returned by preview operations.
    Args:
        api_client (:obj:`ApiClient`): SDC API client.
        response (:obj:`requests.Response`): Command response.
        pipeline_id (:obj:`str`)
        previewer_id (:obj:`str`): Previewer_id.
    """
    def __init__(self, api_client, response, pipeline_id, previewer_id):
        super().__init__(api_client=api_client, response=response)
        self.pipeline_id = pipeline_id
        self.previewer_id = previewer_id

    @property
    @Command.dump_sdc_log_on_error
    def preview(self):
        """The Preview object returned by this preview command.

        Returns:
            (:obj:`sdc_models.Preview`)
        """
        return sdc_models.Preview(pipeline_id=self.pipeline_id,
                                  previewer_id=self.previewer_id,
                                  preview=self.api_client.get_preview_data(
                                      pipeline_id=self.pipeline_id,
                                      previewer_id=self.previewer_id
                                  ).response.json())

    @Command.dump_sdc_log_on_error
    def wait_for_finished(self, timeout_sec=30):
        """Wait for preview to be finished.

        Args:
            timeout_sec (:obj:`int`, optional): Timeout for wait, in seconds. Default: 30
        """
        logger.info('Waiting for preview to be finished...')
        start_waiting_time = time()
        stop_waiting_time = start_waiting_time + timeout_sec

        while time() < stop_waiting_time:
            self.response = self.api_client.get_preview_status(
                pipeline_id=self.pipeline_id,
                previewer_id=self.previewer_id
            ).response
            logger.debug('response.content: %s', self.response.content)
            # Loop back until response content starts coming through.
            if not self.response.content:
                continue

            current_status = self.response.json()['status']
            if current_status == 'FINISHED':
                logger.debug('Pipeline (%s) preview (%s) reached state : %s',
                             self.pipeline_id,
                             self.previewer_id,
                             current_status)
                return self

            sleep(1)

        raise Exception('Timed out after %s seconds while waiting for status FINISHED.')


class ConnectionValidateCommand(Command):
    """Command returned by connection validate operation.

    Args:
        api_client (:py:class:`streamsets.sdk.sdc_api.ApiClient`): SDC API client.
        response (:obj:`requests.Response`): Command response.
        pipeline_id (:obj:`str`): Pipeline ID.
        previewer_id (:obj:`str`): Previewer ID.
    """
    def __init__(self, api_client, response, pipeline_id, previewer_id):
        super().__init__(api_client=api_client, response=response)
        self.pipeline_id = pipeline_id
        self.previewer_id = previewer_id

    @Command.dump_sdc_log_on_error
    def wait_for_validate(self, timeout_sec=120):
        """Wait for validate to be finished.

        Args:
            timeout_sec (:obj:`int`, optional): Timeout for wait, in seconds. Default: 120
        """
        logger.info('Waiting for validate to be finished ...')
        start_waiting_time = time()
        stop_waiting_time = start_waiting_time + timeout_sec

        while time() < stop_waiting_time:
            self.response = self.api_client.get_preview_status(
                pipeline_id=self.pipeline_id,
                previewer_id=self.previewer_id
            ).response
            logger.debug('response.content: %s', self.response.content)
            # Loop back until response content starts coming through.
            if not self.response.content:
                continue

            current_status = self.response.json()['status']
            if current_status not in {'CREATED', 'STARTING', 'RUNNING', 'VALIDATING'}:
                preview = self.api_client.get_preview_data(pipeline_id=self.pipeline_id,
                                                           previewer_id=self.previewer_id)
                self.response = preview.response

                logger.debug('Pipeline (%s) preview (%s) reached state : %s',
                             self.pipeline_id,
                             self.previewer_id,
                             current_status)
                return self

            sleep(1)

        raise Exception('Timed out after {} seconds while waiting for validation.'.format(timeout_sec))
