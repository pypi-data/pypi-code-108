# Copyright 2021 StreamSets Inc.

"""Abstractions to interact with the ST REST API."""

import base64
import datetime
import io
import json
import logging
import os
import urllib3
import zipfile
from collections import namedtuple
from functools import wraps
from time import sleep, time
from urllib.parse import parse_qs, urlencode, urlparse

import javaproperties
import requests
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from . import st_models
from .constants import ENGINE_AUTHENTICATION_METHOD_ASTER, ENGINE_AUTHENTICATION_METHOD_FORM
from .exceptions import BadRequestError, InternalServerError
from .utils import (TRANSFORMER_PIPELINE_TYPE, Version, get_params, join_url_parts, pipeline_json_encoder,
                    wait_for_condition)

logger = logging.getLogger(__name__)

# Any headers that the ST requires for all calls should be added to this dictionary.
REQUIRED_HEADERS = {'X-Requested-By': 'st',
                    'X-SS-REST-CALL': 'true',
                    'content-type': 'application/json'}

DEFAULT_ST_API_VERSION = 1

# The `#:` constructs at the end of assignments are part of Sphinx's autodoc functionality.
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
    API client to communicate with an ST instance.

    Args:
        server_url (:obj:`str`): Complete URL to ST server.
        aster_authentication_token (:obj:`str`, optional): Aster authentication token. Default: ``None``
        aster_server_url (:obj:`str`, optional): Aster server base URL. Default: ``None``
        authentication_method (:obj:`str`, optional): StreamSets Transformer authentication method.
            Default: :py:const:`streamsets.sdk.constants.ENGINE_AUTHENTICATION_METHOD_FORM`.
        api_version (:obj:`int`, optional): The API version. Default: :py:const:`st_api.DEFAULT_ST_API_VERSION`
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
                 authentication_method=ENGINE_AUTHENTICATION_METHOD_FORM,
                 api_version=DEFAULT_ST_API_VERSION,
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
        if self.authentication_method == ENGINE_AUTHENTICATION_METHOD_ASTER:
            if aster_authentication_token is not None and aster_server_url is not None:
                self._register_with_aster_and_login()
            else:
                raise ValueError('aster_authentication_token and aster_server_url are mandatory parameters')
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

        logger.debug('Confirming connectivity to Transformer server ...')

        def st_connectivity_established(api_client):
            try:
                api_client.version = api_client.get_st_info()['version']
                logger.debug('Connected to ST v%s', api_client.version)
                return True
            except requests.exceptions.HTTPError as http_error:
                logger.debug('Call to ST info endpoint failed. Trying again ...')
            except KeyError:
                logger.debug('Invalid ST info received. Trying again ...')
        wait_for_condition(st_connectivity_established, [self])

    def _register_with_aster_and_login(self):
        """Register the Transformer with Aster. Here activation also happens with registration.
        Also perform login as it returns a cookie that needs to be set for any further communication with Transformer.
        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`.
        """
        response = self._get(self.server_url, absolute_endpoint=True)
        # If not registered already, then do register
        # Following check will change after https://issues.streamsets.com/browse/TASER-334
        if 'aregistration.html' in response.url:
            lstate_value = parse_qs(urlparse(response.url).query)['lstate'][0]
            # Obtain the information to start a registration using the lstate query string parameter
            # from the previous response
            response = self._get(endpoint='/v{}/aregistration'.format(self.api_version),
                                 params={'lstate': lstate_value})
            # Make POST to the {}/api/security/oauth/authorize URL to initiate the registration,
            json_data = response.json()['parameters']
            data = urlencode(json_data)
            headers = {'Authorization': 'Bearer {}'.format(self.aster_authentication_token),
                       'Content-Type': 'application/x-www-form-urlencoded'}
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = self._post(endpoint='{}/api/security/oauth/authorize'.format(self.aster_server_url),
                                  absolute_endpoint=True, headers=headers, data=data, is_data_format_json=False)
            # Make a POST call to the Transformer using the query string from the previous response.
            parameters = parse_qs(urlparse(response.url).query)
            # At this point parameters are of the form {'code': ['FvJi3a'], 'state': ['TZlddl']}
            # The following will convert it into the form {'code': 'FvJi3a', 'state': 'TZlddl'}
            params = {key: value[0] for key, value in parameters.items()}
            response = self._post(endpoint='/v{}/aregistration'.format(self.api_version),
                                  params=params)
            # Following assert will change after https://issues.streamsets.com/browse/TASER-335
            assert response.status_code in (200, 302)
            logger.info('Registered Transformer with Aster')

        # Start login sequence
        # Obtain the information to start a registration using the lstate query string parameter
        # from the previous response
        lstate_value = parse_qs(urlparse(response.url).query)['lstate'][0]
        response = self._get(endpoint='/v{}/alogin'.format(self.api_version),
                             params={'lstate': lstate_value})
        # Make POST to the {}/api/security/oauth/authorize URL to initiate the registration,
        # it must be a FORM request (x-www-form-urlencoded)
        json_data = response.json()['parameters']
        data = urlencode(json_data)
        headers = {'Authorization': 'Bearer {}'.format(self.aster_authentication_token),
                   'Content-Type': 'application/x-www-form-urlencoded'}
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = self._post(endpoint='{}/api/security/oauth/authorize'.format(self.aster_server_url),
                              absolute_endpoint=True, headers=headers, data=data, is_data_format_json=False)
        # Make a POST call to the Transformer using the query string from the previous response
        parameters = parse_qs(urlparse(response.url).query)
        # At this point parameters are of the form {'code': ['FvJi3a'], 'state': ['TZlddl']}
        # The following will convert it into the form {'code': 'FvJi3a', 'state': 'TZlddl'}
        params = {key: value[0] for key, value in parameters.items()}
        response = self._post(endpoint='/v{}/alogin'.format(self.api_version),
                              params=params)
        # Following assert will change after https://issues.streamsets.com/browse/TASER-335
        assert response.status_code in (200, 302)
        logger.info('Transformer login complete with Aster')

    def _fetch_tunneling_instance_id(self):
        def _get_tunneling_instance_id(api_client):
            try:
                parsed_uri = urlparse(api_client.server_url)
                sch_url = '{}://{}'.format(parsed_uri.scheme, parsed_uri.netloc)
                end_point = '{}/tunneling/rest/connection/{}'.format(sch_url, parsed_uri.path.split('/tunneling/rest/')[1])
                response = api_client._get(end_point, absolute_endpoint=True)
                self._tunneling_instance_id = response.json()['instanceId']
                logger.debug('Fetched tunneling_instance_id is %s', self._tunneling_instance_id)
                return self._tunneling_instance_id
            except requests.exceptions.HTTPError as http_error:
                logger.debug('Call to fetch tunneling instance id endpoint failed. Trying again ...')
            except KeyError:
                logger.debug('Invalid tunneling instance id received. Trying again ...')
        wait_for_condition(_get_tunneling_instance_id, [self], timeout=300)

    def get_st_info(self):
        """Get ST info.

        Returns:
            A :obj:`dict` of ST system info.
        """
        response = self._get(endpoint='/v{0}/system/info'.format(self.api_version))
        return response.json() if response.content else {}

    def get_transformer_configuration(self):
        """Get all transformer configuration.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`
        """
        response = self._get(endpoint='/v{0}/system/configuration'.format(self.api_version))
        return Command(self, response)

    def get_st_directories(self):
        """Get ST directories.

        Returns:
            A :obj:`dict` of ST directories.
        """
        response = self._get(endpoint='/v{0}/system/directories'.format(self.api_version))
        return response.json() if response.content else {}

    def get_st_log_config(self):
        """Get ST log config.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`
        """
        response = self._get(endpoint='/v{0}/system/log/config'.format(self.api_version))
        return Command(self, response)

    def get_pipeline_committed_offsets(self, pipeline_id, rev=0):
        """Get pipeline committed offsets.

        Args:
            pipeline_id (:obj:`str`)
            rev (:obj:`int`, optional): Default: ``0``

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`
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
            An instance of :py:class:`streamsets.sdk.st_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self', 'pipeline_id', 'body'))
        response = self._post(endpoint='/v{}/pipeline/{}/committedOffsets'.format(self.api_version,
                                                                                  pipeline_id),
                              params=params,
                              data=body)
        return Command(self, response)

    def validate_pipeline(self, pipeline_id, rev=0, timeout=2000, remote=False):
        """Validate a pipeline.

        Args:
            pipeline_id (:obj:`str`)
            rev (:obj:`int`, optional): Revision of the pipeline. Default: 0
            timeout (:obj:`int`, optional): Validation timeout, in milliseconds. Default: 2000
            remote (:obj:`bool`, optional): Remote Validation (i.e. validate on the cluster). Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.ValidateCommand`
        """
        response = self._get(endpoint='/v{}/pipeline/{}/validate'.format(self.api_version, pipeline_id),
                             params={'rev': rev, 'timeout': timeout, 'remote': remote})
        previewer_id = response.json()['previewerId']
        return ValidateCommand(self, response, pipeline_id, previewer_id)

    def reset_origin_offset(self, pipeline_id, rev=0):
        """Reset origin offset.

        Args:
            pipeline_id (:obj:`str`)
            rev (:obj:`int`, optional): Revision of the pipeline. Default: ``0``

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`
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
            get (:obj:`str`, optional): Default:  ``pipeline``

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
            draft (:obj:`bool`, optional): If True, pipeline will be imported but not added to store.
            include_library_definitions (:obj:`bool`, optional): Default: ``None``.
            auto_generate_pipeline_id (:obj:`bool`, optional): If True, pipeline ID will be generated by
                concatenating a UUID to a whitespace-stripped version of the pipeline title. If
                False, the pipeline title will be used as the pipeline ID. Default: ``None``

        Returns:
            A Python object with the JSON response content.
        """
        # TODO: setting includeLibraryDefinitions=False is a workaround to
        # https://issues.streamsets.com/browse/TRANSFORM-443 issue
        params = get_params(parameters=locals(), exclusions=('self', 'pipeline_id', 'pipeline_json'))
        response = self._post(endpoint='/v{}/pipeline/{}/import'.format(self.api_version,
                                                                        pipeline_id),
                              params=params,
                              data=pipeline_json)
        return response.json() if response.content else {}

    def export_pipeline(self, pipeline_id, rev=0, attachment=False, include_library_definitions=False):
        """Export a pipeline.

        Args:
            pipeline_id (:obj:`str`)
            rev (:obj:`int`): Revision of the pipeline.

        Returns:
            A Python object with the JSON response content.
        """

        params = get_params(parameters=locals(), exclusions=('self',
                                                             'pipeline_id'))
        response = self._get(endpoint='/v{0}/pipeline/{1}/export'.format(self.api_version,
                                                                         pipeline_id),
                             params=params)
        return response.json() if response.content else {}

    def export_pipelines(self, body, include_library_definitions=None):
        """Export pipelines.

        Args:
            body (:obj:`str`)
            include_library_definitions (:obj:`bool`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`
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
            An instance of :py:class:`streamsets.sdk.st_api.Command`
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
            An instance of :py:class:`streamsets.sdk.st_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(endpoint='/v{}/pipelines'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def create_pipeline(self, pipeline_title, description=None, auto_generate_pipeline_id=None, draft=None,
                        pipeline_type=TRANSFORMER_PIPELINE_TYPE):
        """Add a new pipeline configuration to the store.

        Args:
            pipeline_title (:obj:`str`)
            description (:obj:`str`, optional): Default: ``None``
            auto_generate_pipeline_id (:obj:`bool`, optional): If True, pipeline ID will be generated by
                concatenating a UUID to a whitespace-stripped version of the pipeline title. If
                False, the pipeline title will be used as the pipeline ID. Default: ``None``
            draft (:obj:`bool`, optional): If True, pipeline will be created but not added to ST store.
                Default: ``None``
            pipeline_type (:obj:`str`, optional): Default: ``'BATCH'``.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`
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

    def create_fragment(self, title, description=None, draft=None, execution_mode=None, body=None):
        """Add a new pipeline configuration to the store.

        Args:
            title (:obj:`str`)
            description (:obj:`str`, optional): Default: ``None``
            draft (:obj:`bool`, optional): If True, fragment will be created but not added to Transformer store.
                Default: ``None``
            execution_mode (:obj:`str`, optional): Default: `` None``
            body (:obj:`dict`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self', 'title'))
        response = self._put(endpoint='/v{}/fragment/{}'.format(self.api_version, title),
                             params=params,
                             data=body,
                             is_data_format_json=False)
        return Command(self, response)

    def delete_pipeline(self, pipeline_id):
        """Delete a pipeline configuration.

        Args:
            pipeline_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`
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
            An instance of :py:class:`streamsets.sdk.st_api.StartPipelineCommand`
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
            An instance of :py:class:`streamsets.sdk.st_api.PipelineCommand`
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
            An instance of :py:class:`streamsets.sdk.st_api.Command`
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
            An instance of :py:class:`streamsets.sdk.st_api.Command`
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
            The JSON response from pipeline metrics.
        """
        response = self._get(endpoint='/v{0}/pipeline/{1}/metrics'.format(self.api_version,
                                                                          pipeline_id),
                             params={'rev': rev})
        return response.json() if response.content else {}

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

    def get_activation(self):
        """Get activation.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`.
        """
        response = self._get(endpoint='/v{0}/activation'.format(self.api_version))
        return Command(self, response)

    def activate(self, activation_key):
        """Activate Transformer using the passed activation key.

        Args:
            activation_key (:obj:`str`) The activation key.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`.
        """
        response = self._post(endpoint='/v{}/activation'.format(self.api_version),
                              data=activation_key,
                              is_data_format_json=False,
                              headers={'content-type': 'text/plain'})
        return Command(self, response)

    def get_license(self, license_endpoint, data, oauth_endpoint, client_id, client_secret):
        """Get a license which will be used for activation - generally by sales.

        Args:
            license_endpoint (:obj:`str`) The endpoint where to get license from.
            data (:obj:`dict`): Data to be sent along with the post request.
            oauth_endpoint (:obj:`str`): End point to fetch access token.
            client_id (:obj:`str`): client_id to be sent to the oauth_end_point.
            client_secret (:obj:`str`): client_secret to be sent to the oauth_end_point.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`.
        """
        # Get access_token
        payload = {'client_id': client_id,
                   'client_secret': client_secret,
                   'grant_type': 'client_credentials',
                   'audience': 'https://license.streamsets'}
        response = self._post(endpoint=oauth_endpoint,
                              absolute_endpoint=True,
                              data=payload)
        if not response.content:
            raise 'No access token received with given client_id and client_secret'

        # Now get license using the access token
        response_json = response.json()
        headers = {'Authorization': "{} {}".format(response_json['token_type'],
                                                   response_json['access_token']),
                   'Content-Type': 'application/json'}
        response = requests.post(license_endpoint, data=json.dumps(data or {}), headers=headers)
        response.raise_for_status()
        return Command(self, response)

    def register(self, registration_endpoint, data):
        """Register the Transformer. Here the activation key is sent to the email specified in data.

        Args:
            registration_endpoint (:obj:`str`) The endpoint where to register Transformer.
            data (:obj:`dict`): Data to be sent along with the post request.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`.
        """
        response = self._post(endpoint=registration_endpoint, absolute_endpoint=True, data=data)
        return Command(self, response)

    def get_transformer_id(self):
        """
        Get Transformer ID.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`.
        """
        response = self._get(endpoint='/v{0}/system/info/id'.format(self.api_version))
        return Command(self, response)

    def opt_for_system_stats(self, opt):
        """
        Opt In/Out for Statistics.

        Args:
            opt (:obj:`str`, optional): extra_message, Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`.
        """
        response = self._post(endpoint='/v{0}/system/stats'.format(self.api_version),
                              params={'active': opt})
        return Command(self, response)

    def get_system_stats(self):
        """
        Get system Statistics.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`.
        """
        response = self._get(endpoint='/v{0}/system/stats'.format(self.api_version))
        return Command(self, response)

    def get_jmx_metrics(self):
        """Get Transformer JMX metrics.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`.
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
            An instance of :py:class:`streamsets.sdk.st_api.Command`.
        """
        current_user = self.get_current_user()
        endpoint = '/v{}/usermanagement/users/{}/changePassword'
        response = self._post(endpoint=endpoint.format(self.api_version, current_user['user']),
                              data=data_json)
        return Command(self, response)

    def get_logs(self, ending_offset=-1, extra_message=None, pipeline=None, severity=None):
        """Get ST logs.

        Args:
            ending_offset (:obj:`int`, optional): ending_offset, Default: ``-1``.
            extra_message (:obj:`str`, optional): extra_message, Default: ``None``.
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`, optional): The pipeline instance,
                                                                                 Default: ``None``.
            severity (:obj:`str`, optional): severity, Default: ``None``.

        Returns:
            The JSON response containing information about the logs.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(endpoint='/v{0}/system/logs'.format(self.api_version),
                             params=params)
        return response.json() if response.content else {}

    def get_driver_logs(self, pipeline_id=None, run_count=None, ending_offset=-1):
        """Get pipeline driver log contents.

        Args:
            pipeline_id (:obj:`str`)
            run_count (:obj:`int`, optional): run_count, Default: ``None``.
            ending_offset (:obj:`int`, optional): ending_offset, Default: ``-1``.

        Returns:
            The TEXT response containing information about the pipeline driver logs.
        """
        params = get_params(parameters=locals(), exclusions=('self', pipeline_id))
        response = self._get(endpoint='/v{}/pipeline/{}/driverLogs'.format(self.api_version, pipeline_id),
                             params=params)
        return response.text

    def stop_pipeline(self, pipeline_id, rev=0):
        """Stop a pipeline.

        Args:
            pipeline_id (:obj:`str`)
            rev (:obj:`int`, optional): Revision of the pipeline. Default: ``0``

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.StopPipelineCommand`
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
            An instance of :py:class:`streamsets.sdk.st_api.StopPipelineCommand`
        """
        response = self._post(endpoint='/v{}/pipeline/{}/forceStop'.format(self.api_version,
                                                                           pipeline_id),
                              params={'rev': rev})
        return StopPipelineCommand(self, response)

    def get_definitions(self):
        """Get ST definitions.

        Returns:
            A :obj:`list` of stage definition :obj:`dict` instances.
        """
        response = self._get(endpoint='/v{0}/definitions'.format(self.api_version))
        return response.json()

    def run_pipeline_preview(self, pipeline_id, rev=0,
                             batches=1, batch_size=10, skip_targets=True,
                             end_stage=None, timeout=2000,
                             stage_outputs_to_override_json=None,
                             remote=None):
        """Run pipeline preview.
        Args:
            pipeline_id (:obj:`str`)
            rev (:obj:`int`, optional)
            batches (:obj:`int`, optional)
            batch_size (:obj:`int`, optional)
            skip_targets (:obj:`bool`, optional)
            end_stage (:obj:`str`, optional)
            timeout (:obj:`int`, optional)
            stage_outputs_to_override_json (:obj:`str`, optional)
            remote (:obj:`bool`, optional)
        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.PreviewCommand`
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
            An instance of :py:class:`streamsets.sdk.st_api.Command`
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
            An instance of :py:class:`streamsets.sdk.st_api.PreviewCommand`
        """
        response = self._get(endpoint='/v{}/pipeline/{}/preview/{}'.format(self.api_version,
                                                                           pipeline_id,
                                                                           previewer_id))
        return PreviewCommand(self, response, pipeline_id, previewer_id)

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
            An instance of :py:class:`streamsets.sdk.st_api.Command`
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
            An instance of :py:class:`streamsets.sdk.st_api.Command`
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

    def get_stage_libraries_list(self, repo_url, installed_only):
        """Get stage libraries list.
        Args:
            repo_url (:obj:`str`): repo url
            installed_only (:obj:`boolean`): installed only libraries

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(endpoint='/v{}/stageLibraries/list'.format(self.api_version),
                             params=params)
        return Command(self, response)

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

    def _post(self, endpoint, absolute_endpoint=False, params={}, data=None, headers=None, is_data_format_json=True):
        url = endpoint if absolute_endpoint else join_url_parts(self.server_url, '/rest', endpoint)
        if is_data_format_json:
            # When we serialize to JSON, we define a default to enable handling of objects (e.g.
            # :py:class:`streamsets.sdk.models.Configuration` embedded in the data).
            data = json.dumps(data, default=pipeline_json_encoder) if data else None

        if self._tunneling_instance_id:
            params.update({'TUNNELING_INSTANCE_ID': self._tunneling_instance_id})
        response = self.session.post(url, params=params, data=data, headers=headers)
        self._handle_http_error(response)
        return response

    def _put(self, endpoint, params={}, data=None):
        url = join_url_parts(self.server_url, '/rest', endpoint)
        if self._tunneling_instance_id:
            params.update({'TUNNELING_INSTANCE_ID': self._tunneling_instance_id})
        response = self.session.put(url, params=params, data=data)
        self._handle_http_error(response)
        return response

    def _handle_http_error(self, response):
        """Specific error handling for ST, to make better error reporting where applicable."""
        if response.status_code == 500:
            raise InternalServerError(response)
        elif response.status_code == 400:
            raise BadRequestError(response)

        # Delegating to response object error handling as last resort.
        response.raise_for_status()


class Command:
    """Command to allow users to interact with commands submitted through ST REST API.

    Args:
        api_client (:py:class:`streamsets.sdk.st_api.ApiClient`): ST API client.
        response (:py:class:`requests.Response`): Command reponse.
    """
    def __init__(self, api_client, response):
        self.api_client = api_client
        self.response = response

    def dump_st_log_on_error(*dec_args, **dec_kwargs):  # pylint: disable=no-method-argument
        """A Python Decorator to log ST when errors happen.
        Args:
            *dec_args (:obj:, optional): Optional non key-worded arguments to be passed.
            **dec_kwargs (:obj:, optional): Optional key-worded arguments to be passed, such as `all`. `all` will
                log complete ST.
        """
        def outer_func(func):
            @wraps(func)
            def wrapped(self, *args, **kwargs):
                log_time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')
                try:
                    return func(self, *args, **kwargs)
                except Exception:
                    if self.api_client.dump_log_on_error:
                        st_log_obj = st_models.Log(self.api_client.get_logs())
                        st_log = (st_log_obj if dec_kwargs.get('all') else st_log_obj.after_time(log_time_now))
                        if st_log:
                            logger.error('Error during `%s` call. ST log follows ...', func.__name__)
                            print('------------------------- ST log - Begins -----------------------')
                            print(st_log)
                            print('------------------------- ST log - Ends -------------------------')
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


class StartError(StatusError):
    """Pipeline start error."""
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


class InvalidError(StatusError):
    """Invalid stage config error."""
    pass


# A simple mapping between error statuses from the ST API and exceptions to raise.
ERROR_STATUSES = {
    'START_ERROR': StartError,
    'RUNNING_ERROR': RunningError,
    'RUN_ERROR': RunError,
    'CONNECT_ERROR': ConnectError,
    'INVALID': InvalidError
}


class PipelineCommand(Command):
    """Pipeline Command to allow users to interact with commands submitted through ST REST API.

    Args:
        api_client (:py:class:`streamsets.sdk.st_api.ApiClient`): ST API client.
        response (:py:class:`requests.Response`): Command reponse.
    """

    @Command.dump_st_log_on_error
    def wait_for_status(self, status, ignore_errors=False, timeout_sec=300, time_between_checks=1):
        """Wait for pipeline status.
        Args:
            status (:obj:`str`): Pipeline status.
            ignore_errors(:obj:`boolean`): If set to true then this method will not throw
                exception if an error state is detected. Particularly useful if the caller
                needs to wait on one of the terminal error states.
            timeout_sec (:obj:`int`): Timeout for wait, in seconds. Default: 300
            time_between_checks (:obj:`int`, optional): Time to sleep between status checks, in seconds. Default: 1
        """
        logger.info('Waiting for status %s ...', status)

        # we will only log response status a max number of times - evenly spread out within timeout_sec or
        # if the response status changes
        log_iterator_count = _iterations_between_sleep(timeout_sec, time_between_checks, 20)
        log_counter = 0

        start_waiting_time = time()
        stop_waiting_time = start_waiting_time + timeout_sec

        while time() < stop_waiting_time:
            try:
                pipeline_id = self.response.json()['pipelineId']
            except KeyError:
                pipeline_id = self.response.json()['name']

            log_counter += 1
            if log_counter == 1 or current_status != self.response.json()['status']:
                logger.debug('Status of pipeline %s is %s ...', pipeline_id, self.response.json()['status'])
            elif log_counter == log_iterator_count:
                log_counter = 0

            current_status = self.response.json()['status']
            if (isinstance(status, list) and current_status in status) or current_status == status:
                logger.info('Pipeline %s reached status %s (took %.2f s).',
                            pipeline_id,
                            current_status,
                            time() - start_waiting_time)
                break
            elif not ignore_errors and current_status in ERROR_STATUSES:
                raise ERROR_STATUSES.get(current_status)(self.response.json())
            else:
                sleep(time_between_checks)
                self.response = self.api_client.get_pipeline_status(pipeline_id).response
        else:
            raise Exception('Timed out after %s seconds while waiting for status %s.',
                            timeout_sec,
                            status)


class StartPipelineCommand(PipelineCommand):
    """Pipeline start command to allow users to interact with commands submitted
    through ST REST API.

    Args:
        api_client (:py:class:`streamsets.sdk.st_api.ApiClient`): ST API client.
        response (:py:class:`requests.Response`): Command reponse.
    """
    def wait_for_finished(self, timeout_sec=300, time_between_checks=1):
        """
        Wait for pipeline to be finished.
        Args:
            timeout_sec (int): Timeout for wait, in seconds. Default: 300
            time_between_checks (:obj:`int`, optional): Time to sleep between status checks, in seconds. Default: 1
        """
        self.wait_for_status(status='FINISHED', timeout_sec=timeout_sec, time_between_checks=time_between_checks)

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
    @Command.dump_st_log_on_error
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
            if current_status in ERROR_STATUSES:
                raise ERROR_STATUSES.get(current_status)(self.response.json())

            current_counters_metrics = self.api_client.get_pipeline_metrics(
                pipeline_id=pipeline_id
            ).get('counters', {})

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
    through ST REST API.

    Args:
        api_client (:py:class:`streamsets.sdk.st_api.ApiClient`): ST API client.
        response (:py:class:`requests.Response`): Command response.
        time_between_checks (:obj:`int`, optional): Time to sleep between status checks, in seconds. Default: 1
    """
    def wait_for_stopped(self, timeout_sec=300, time_between_checks=1):
        """
        Wait for pipeline to be stopped.
        Args:
            timeout_sec (int): Timeout for wait, in seconds. Default: 300
            time_between_checks (:obj:`int`, optional): Time to sleep between status checks, in seconds. Default: 1
        """
        self.wait_for_status(status='STOPPED', timeout_sec=timeout_sec, time_between_checks=time_between_checks)


class ValidateCommand(Command):
    """Command returned by validate operations.
    Args:
        api_client (:obj:`ApiClient`): ST API client.
        response (:obj:`requests.Response`): Command response.
        pipeline_id (:obj:`str`)
        previewer_id (:obj:`str`): Previewer_id.
    """
    def __init__(self, api_client, response, pipeline_id, previewer_id):
        super().__init__(api_client=api_client, response=response)
        self.pipeline_id = pipeline_id
        self.previewer_id = previewer_id

    @Command.dump_st_log_on_error
    def wait_for_validate(self, timeout_sec=500, time_between_checks=2):
        """Wait for validate to be finished.

        Args:
            timeout_sec (:obj:`int`, optional): Timeout for wait, in seconds. Default: 500
            time_between_checks (:obj:`int`, optional): Time to sleep between status checks, in seconds. Default: 2
        """
        logger.info('Waiting for validate to be finished ...')

        # we will only log the response content a max number of times - evenly spread out within timeout_sec or
        # if the response status changes
        log_iterator_count = _iterations_between_sleep(timeout_sec, time_between_checks, 10)
        log_counter = 0

        start_waiting_time = time()
        stop_waiting_time = start_waiting_time + timeout_sec

        while time() < stop_waiting_time:
            self.response = self.api_client.get_preview_status(
                pipeline_id=self.pipeline_id,
                previewer_id=self.previewer_id
            ).response

            # Loop back until response content starts coming through.
            if not self.response.content:
                continue

            log_counter += 1
            if log_counter == 1 or current_status != self.response.json()['status']:
                logger.debug('response.content: %s', self.response.content)
            elif log_counter == log_iterator_count:
                log_counter = 0

            current_status = self.response.json()['status']
            if current_status != 'VALIDATING' and current_status != 'STARTING':
                if current_status != 'VALID':
                    preview = self.api_client.get_preview_data(pipeline_id=self.pipeline_id,
                                                               previewer_id=self.previewer_id)
                    self.response = preview.response

                logger.info('Pipeline (%s) validate (%s) reached state: %s (took %.2f s)',
                            self.pipeline_id,
                            self.previewer_id,
                            current_status,
                            time() - start_waiting_time)
                return self

            sleep(time_between_checks)

        raise Exception('Timed out after %s seconds while waiting for validation.', timeout_sec)


class PreviewCommand(Command):
    """Command returned by preview operations.
    Args:
        api_client (:obj:`ApiClient`): ST API client.
        response (:obj:`requests.Response`): Command response.
        pipeline_id (:obj:`str`)
        previewer_id (:obj:`str`): Previewer_id.
    """
    def __init__(self, api_client, response, pipeline_id, previewer_id):
        super().__init__(api_client=api_client, response=response)
        self.pipeline_id = pipeline_id
        self.previewer_id = previewer_id

    @property
    @Command.dump_st_log_on_error
    def preview(self):
        """The Preview object returned by this preview command.

        Returns:
            (:obj:`st_models.Preview`)
        """
        return st_models.Preview(pipeline_id=self.pipeline_id,
                                 previewer_id=self.previewer_id,
                                 preview=self.api_client.get_preview_data(
                                    pipeline_id=self.pipeline_id,
                                    previewer_id=self.previewer_id
                                 ).response.json())

    @Command.dump_st_log_on_error
    def wait_for_finished(self, timeout_sec=30, time_between_checks=2):
        """Wait for preview to be finished.

        Args:
            timeout_sec (:obj:`int`, optional): Timeout for wait, in seconds. Default: 30
            time_between_checks (:obj:`int`, optional): Time to sleep between status checks, in seconds. Default: 2
        """
        logger.info('Waiting for preview to be finished...')

        # we will only log the response content a max number of times - evenly spread out within timeout_sec or
        # if the response status changes
        log_iterator_count = _iterations_between_sleep(timeout_sec, time_between_checks, 10)
        log_counter = 0

        start_waiting_time = time()
        stop_waiting_time = start_waiting_time + timeout_sec

        while time() < stop_waiting_time:
            self.response = self.api_client.get_preview_status(
                pipeline_id=self.pipeline_id,
                previewer_id=self.previewer_id
            ).response

            # Loop back until response content starts coming through.
            if not self.response.content:
                continue

            log_counter += 1
            if log_counter == 1 or current_status != self.response.json()['status']:
                logger.debug('response.content: %s', self.response.content)
            elif log_counter == log_iterator_count:
                log_counter = 0

            current_status = self.response.json()['status']
            if current_status == 'FINISHED':
                logger.info('Pipeline (%s) preview (%s) reached state: %s (took %.2f s)',
                            self.pipeline_id,
                            self.previewer_id,
                            current_status,
                            time() - start_waiting_time)
                return self
            elif current_status in ERROR_STATUSES:
                raise ERROR_STATUSES.get(current_status)(self.response.json())

            sleep(time_between_checks)
            self.response = self.api_client.get_pipeline_status(
                pipeline_id=self.pipeline_id
            ).response

        raise Exception('Timed out after %s seconds while waiting for status FINISHED or %s',
                        timeout_sec, ', '.join(ERROR_STATUSES.keys()))


def _iterations_between_sleep(time_window_sec, sleep_sec, number_of_responses):
    # A helper function which will compute number of iterations between each sleep_sec spread within
    # a time_window_sec, considering a maximum number_sleep_sec to happen within that time_window_sec
    approx_iterations = int(time_window_sec / sleep_sec)  # approx loop iterations
    return int(approx_iterations / number_of_responses)
