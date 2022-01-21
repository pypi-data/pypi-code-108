# Copyright IBM Corp. 2021. All Rights Reserved.

import base64
import io
import json
import os
import warnings
from abc import abstractmethod
from collections import abc
from enum import Enum
from functools import wraps
from typing import cast, ClassVar, Mapping, Union, Optional, Any, Callable, \
    Tuple, Protocol
from urllib.parse import urljoin, quote

import requests
import attr
from attr import attrs, fields_dict, NOTHING
from ibm_cloud_sdk_core import BaseService, DetailedResponse
from ibm_cloud_sdk_core.authenticators import Authenticator, IAMAuthenticator, \
    CloudPakForDataAuthenticator, BearerTokenAuthenticator
import ibm_boto3
from ibm_botocore.client import Config

from .client_errors import JsonParsingError, MissingValueError, \
    OfCpdPathError, NoWmlInstanceError, WmlServiceNameUnknownTypeError, \
    WmlServiceNameNoPrefixError, WmlServiceCNameNotValidError, \
    PublicCloudOnlyError, FilesResultsNotSupportedError, NoSuchOverloadError, \
    WmlUnknownAuthMethodError
from .cpd_paths import CpdScope
from .utils import validate_type, \
    get_storage_config_field, get_scope_response_field, get_credentials_field


def public_cloud_only(fn: Callable) -> Callable:
    @wraps(fn)
    def inner(self: 'WSPipelines', *args, **kwargs):
        if not self.is_public:
            raise PublicCloudOnlyError("Function", fn.__name__)
        return fn(self, *args, **kwargs)
    return inner

class AuthMethod(Enum):
    APIKEY = 'apikey'
    BEARER_TOKEN = 'bearer_token'
    ANY = 'any'

class WSPipelines(BaseService):
    """Watson Studio Pipelines client

    Communicates with Watson Studio Pipelines to provide some high-level utilities.

    Arguments:
        apikey (str): API key the authenticator should be constructed from

    Keyword Arguments:
        service_name (str): name of the service used
        url (str): url of the service the client should communicate with
    """

    DEFAULT_SERVICE_URL = "https://api.dataplatform.cloud.ibm.com"
    DEFAULT_SERVICE_NAME = 'watson-studio-pipelines'

    DEFAULT_CPD_API_URL = "https://api.dataplatform.cloud.ibm.com"

    SDK_NAME = 'ibm-watson-studio-pipelines'


    @classmethod
    def new_instance(cls, *, service_name: str = None, url: str = None) -> 'WSPipelines':
        """
        Return a new Watson Studio Pipelines client for default settings.
        """
        return cls(service_name=service_name, url=url)

    @classmethod
    def from_apikey(cls, apikey: str = None, *, service_name: str = None, url: str = None) -> 'WSPipelines':
        """
        Return a new Watson Studio Pipelines client for the specified API key.
        """
        return cls(
            apikey=apikey,
            auth_method=AuthMethod.APIKEY,
            service_name=service_name,
            url=url,
        )

    @classmethod
    def from_token(cls, bearer_token: str = None, *, service_name: str = None, url: str = None) -> 'WSPipelines':
        """
        Return a new Watson Studio Pipelines client for the specified bearer token.
        """
        return cls(
            bearer_token=bearer_token,
            auth_method=AuthMethod.BEARER_TOKEN,
            service_name=service_name,
            url=url,
        )

    def __init__(
        self,
        apikey: str = None,
        *,
        bearer_token: str = None,
        service_name: str = None,
        url: str = None,
        auth_method: AuthMethod = None,
    ):

        url = self._get_cpd_api_url(url)
        validate_type(url, "url", str)

        authenticator, is_public = self._get_authenticator(
            auth_method,
            apikey=apikey,
            bearer_token=bearer_token,
            url=url,
        )

        if service_name is None:
            service_name = self.DEFAULT_SERVICE_NAME

        super().__init__(
            service_url=url,
            authenticator=authenticator,
            disable_ssl_verification=not is_public,
        )
        self.authenticator = authenticator
        self.configure_service(service_name)
        self.is_public = is_public

    def _get_authenticator(
            self,
            auth_method: Optional[AuthMethod],
            apikey: Optional[str],
            bearer_token: Optional[str],
            url: str,
    ) -> Tuple[Authenticator, bool]:
        def censor_value(value: Optional[Any]) -> Optional[str]:
            if value is None:
                return None
            return '...'

        def no_such_overload() -> NoSuchOverloadError:
            class_name = type(self).__name__
            kwargs = {
                'apikey': censor_value(apikey),
                'bearer_token': censor_value(bearer_token),
                'auth_method': auth_method,
            }
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return NoSuchOverloadError(class_name, [], kwargs)

        if apikey is not None and bearer_token is not None:
            raise no_such_overload()

        if auth_method == AuthMethod.APIKEY:
            if bearer_token is not None:
                raise no_such_overload()
            if apikey is None:
                apikey = os.environ.get('APIKEY', None)
            if apikey is None:
                raise MissingValueError('APIKEY')
            return self._get_authenticator_from_api_key(apikey, url)

        elif auth_method == AuthMethod.BEARER_TOKEN:
            if apikey is not None:
                raise no_such_overload()
            if bearer_token is None:
                bearer_token = os.environ.get('USER_ACCESS_TOKEN')
            if bearer_token is None:
                raise MissingValueError('USER_ACCESS_TOKEN')
            return self._get_authenticator_from_bearer_token(bearer_token, url)

        elif auth_method == AuthMethod.ANY or auth_method is None:
            if apikey is not None:
                return self._get_authenticator_from_api_key(apikey, url)
            elif bearer_token is not None:
                return self._get_authenticator_from_bearer_token(bearer_token, url)

            apikey = os.environ.get('APIKEY', None)
            if apikey is not None:
                return self._get_authenticator_from_api_key(apikey, url)

            bearer_token = os.environ.get('USER_ACCESS_TOKEN')
            if bearer_token is not None:
                return self._get_authenticator_from_bearer_token(bearer_token, url)

            # should provide either APIKEY or USER_ACCESS_TOKEN, usually APIKEY
            raise MissingValueError('APIKEY')
        else:
            raise no_such_overload()

    def _get_iam_url(self, url: str) -> Tuple[str, bool]:
        validate_type(url, "url", str)
        if not url.startswith("https://"):
            warnings.warn("'url' doesn't start with https")

        url_to_iam_url = {
            "https://api.dataplatform.dev.cloud.ibm.com": "https://iam.test.cloud.ibm.com/identity/token",
            "https://api.dataplatform.test.cloud.ibm.com": "https://iam.cloud.ibm.com/identity/token",
            "https://api.dataplatform.cloud.ibm.com": "https://iam.cloud.ibm.com/identity/token"
        }
        is_public = True
        iam_url = url_to_iam_url.get(url)
        if iam_url is None:
            # assume it's CPD
            is_public = False
            iam_url = url + "/icp4d-api/v1/authorize"
        return iam_url, is_public

    def _get_authenticator_from_api_key(self, apikey: str, url: str) -> Tuple[Authenticator, bool]:
        validate_type(apikey, "api_key", str)
        iam_url, is_public = self._get_iam_url(url)
        if is_public:
            auth = IAMAuthenticator(apikey, url=iam_url)
        else:
            auth = CloudPakForDataAuthenticator("admin", url=iam_url, apikey=apikey, disable_ssl_verification=True)
        self.auth_method = AuthMethod.APIKEY
        # for backwards-compatibility, WSPipelines directly gets the `apikey` field
        self.apikey = apikey
        return auth, is_public

    def _get_authenticator_from_bearer_token(self, bearer_token: str, url: str) -> Tuple[Authenticator, bool]:
        validate_type(bearer_token, "bearer_token", str)
        iam_url, is_public = self._get_iam_url(url)
        auth = BearerTokenAuthenticator(bearer_token=bearer_token)
        self.auth_method = AuthMethod.BEARER_TOKEN
        # to stay consistent with `apikey`, WSPipelines directly gets the `bearer_token` field
        self.bearer_token = bearer_token
        return auth, is_public

    @classmethod
    def get_output_artifact_map(cls) -> Mapping[str, str]:
        """Get output artifacts key-value map from env-var OF_OUTPUT_ARTIFACTS."""
        output_artifacts = os.environ.get('OF_OUTPUT_ARTIFACTS', None)
        if output_artifacts is None:
            raise MissingValueError("OF_OUTPUT_ARTIFACTS")

        try:
            output_artifacts = json.loads(output_artifacts)
        except json.decoder.JSONDecodeError as ex:
            # could it be base64?
            try:
                pad_base64 = lambda s: s + '=' * (-len(s) % 4)
                output_artifacts = base64.b64decode(pad_base64(output_artifacts))
                output_artifacts = json.loads(output_artifacts)
            except:
                # if it has been decoded, show the decoded value
                raise JsonParsingError(output_artifacts, ex)

        validate_type(output_artifacts, "OF_OUTPUT_ARTIFACTS", abc.Mapping)
        for output_name, output_artifact in output_artifacts.items():
            validate_type(output_artifact, f"OF_OUTPUT_ARTIFACTS[{output_name}]", str)
        output_artifacts = cast(Mapping[str, str], output_artifacts)
        return output_artifacts

    def get_project(self, scope_id: str, *, context: Optional[str] = None) -> dict:
        """Get project of given ID."""
        uri = urljoin("/v2/projects/", scope_id)
        scope = self._get_scope_from_uri(uri, context=context)
        return scope

    def get_space(self, scope_id: str, *, context: Optional[str] = None) -> dict:
        """Get space of given ID."""
        uri = urljoin("/v2/spaces/", scope_id)
        scope = self._get_scope_from_uri(uri, context=context)
        return scope

    def _get_scope_from_uri(self, uri: str, *, context: Optional[str] = None):
        headers = {
            "Accept": "application/json",
        }
        params = {}
        if context is not None:
            params["context"] = context

        scope_request = self.prepare_request('GET', uri, headers=headers, params=params)
        # BaseService has some type signature problems here
        scope_request = cast(requests.Request, scope_request)

        scope_response = self.send(scope_request)

        if isinstance(scope_response.result, dict):
            scope = scope_response.result
        else:
            try:
                scope = json.loads(scope_response.result.content)
            except json.decoder.JSONDecodeError as ex:
                if hasattr(scope_response.result, 'content'):
                    raise JsonParsingError(scope_response.result.content, ex)
                else:
                    raise JsonParsingError(scope_response.result, ex)
        return scope

    def _get_cpd_api_url(self, url: str = None) -> str:
        if url is not None:
            return url

        url = os.environ.get('OF_CPD_API_URL', None)
        if url is not None:
            validate_type(url, "OF_CPD_API_URL", str)
            return url

        url = self.DEFAULT_CPD_API_URL
        validate_type(url, "DEFAULT_CPD_API_URL", str)
        return url

    def get_scope(
        self,
        cpd_scope: Optional[Union[str, CpdScope]] = None
    ) -> dict:
        """Get scope given its CPDPath."""
        cpd_scope = self.get_scope_cpdpath(cpd_scope)

        class ScopeGetter(Protocol):
            @abstractmethod
            def __call__(self, scope_id: str, *, context: Optional[str] = None) -> dict: ...

        scope_type_map: Mapping[str, ScopeGetter] = {
            'projects': self.get_project,
            'spaces': self.get_space,
        }

        scope_getter = scope_type_map.get(cpd_scope.scope_type(), None)
        if scope_getter is None:
            li = ', '.join(scope_type_map.keys())
            msg = "Handling scopes other than {} is not supported yet!".format(li)
            raise NotImplementedError(msg)

        ctx = cpd_scope.context()
        if ctx == '':
            ctx = None

        if cpd_scope.scope_id() is None:
            raise RuntimeError("CpdScope in get_scope cannot be query-type")

        scope = scope_getter(cpd_scope.scope_id(), context=ctx)
        return scope

    @classmethod
    def _extract_storage_properties(
        cls,
        scope_response: dict
    ) -> dict:
        props = get_scope_response_field(scope_response, 'entity.storage.properties', dict)
        return props

    @classmethod
    def _extract_storage_guid(
            cls,
            scope_response: dict
    ) -> str:
        guid = get_scope_response_field(scope_response, 'entity.storage.guid', str)
        return guid

    @public_cloud_only
    def get_wml_credentials(
        self,
        cpd_scope: Optional[Union[str, CpdScope]] = None
    ) -> dict:
        """Get WML credentials given scope's CPDPath.

        Note: this is a public-cloud-only feature. For CPD, only the address
        and API key are needed, no credentials."""
        # make sure cpd_scope is not-None, as _extract_wml_creds_from_scope_response
        # needs it that way
        cpd_scope = self.get_scope_cpdpath(cpd_scope)
        scope_response = self.get_scope(cpd_scope)

        wml_credentials = self._extract_wml_creds_from_scope_response(
            cpd_scope,
            scope_response
        )
        return wml_credentials.to_dict()

    def _extract_wml_creds_from_scope_response(
        self,
        cpd_scope: CpdScope,
        scope_response: dict
    ) -> 'WmlCredentials':
        computed = get_scope_response_field(
            scope_response, "entity.compute", list, mandatory=False
        )

        data = None
        for el in computed or []:
            if 'type' in el and el['type'] == 'machine_learning':
                data = el
                break

        if data is None:
            raise NoWmlInstanceError(cpd_scope)

        return self._extract_wml_creds_from_computed(cpd_scope, data)

    def _extract_wml_creds_from_computed(
        self,
        cpd_scope: CpdScope,
        computed: dict
    ) -> 'WmlCredentials':
        guid = get_credentials_field(computed, "guid", str)
        name = get_credentials_field(computed, "name", str)
        crn = get_credentials_field(computed, "crn", str)
        url = self._get_wml_url_from_wml_crn(crn)

        if hasattr(self, 'apikey'):
            auth = WmlCredentialsApiKey(self.apikey)
        elif hasattr(self, 'bearer_token'):
            auth = WmlCredentialsBearerToken(self.bearer_token)
        else:
            raise WmlUnknownAuthMethodError(cpd_scope, str(self.auth_method.value))

        return WmlCredentials(
            guid = guid,
            name = name,
            url = url,
            auth = auth,
        )

    def _get_wml_url_from_wml_crn(self, crn: str) -> str:
        wml_prod = 'https://{}.ml.cloud.ibm.com'
        wml_qa = 'https://yp-qa.ml.cloud.ibm.com'
        wml_staging = 'https://{}.ml.test.cloud.ibm.com'
        wml_service_name = 'pm-20'
        wml_service_name_devops = 'pm-20-devops'
        platform_qa_url_host = 'api.dataplatform.test.cloud.ibm.com'

        parts = crn.split(':')

        cname = parts[2]
        service_name = parts[4]
        location = parts[5]

        if not service_name.startswith(wml_service_name):
            raise WmlServiceNameNoPrefixError(crn, service_name, wml_service_name)

        if cname == 'bluemix':
            if platform_qa_url_host in self.service_url:
                return wml_qa
            else:
                return wml_prod.format(location)
        elif cname == 'staging':
            if service_name == wml_service_name:
                return wml_staging.format('us-south')
            elif service_name == wml_service_name_devops:
                return wml_staging.format('wml-fvt')
            else:
                raise WmlServiceNameUnknownTypeError(crn, service_name)
        else:
            raise WmlServiceCNameNotValidError(crn, cname, ['bluemix', 'staging'])

    @public_cloud_only
    def get_storage_credentials(
        self,
        cpd_scope: Optional[Union[str, CpdScope]] = None
    ) -> dict:
        """Get storage credentials given scope's CPDPath.

        Note: this is a public-cloud-only feature. For CPD, only the address
        and API key are needed, no credentials."""
        scope_response = self.get_scope(cpd_scope)
        props = self._extract_storage_properties(scope_response)

        cos_credentials = StorageCredentialsFull.from_storage_properties(props)
        return cos_credentials.to_dict()

    @classmethod
    def get_scope_cpdpath(
        cls,
        cpd_scope: Optional[Union[str, CpdScope]] = None
    ) -> CpdScope:
        """Get the scope as CpdScope.

         The operation performed depends on the data type passed:
         * given ``None``, the default scope will be retrieved from environmental variable
         * given a string, it will be parsed to a ``CpdScope``
         * given a ``CpdScope``, it will be returned as-is (i.e. it's a no-op)

         Mostly useful with zero arguments (to retrieve the default scope)
         or when handling ``Union[str, CpdScope]``."""
        # if cpd_scope is None --- get it from env-var
        if cpd_scope is None:
            cpd_scope = os.environ.get('OF_CPD_SCOPE', None)
            if cpd_scope is None:
                raise MissingValueError("OF_CPD_SCOPE")

        # if cpd_scope is str --- parse it
        if isinstance(cpd_scope, str):
            try:
                cpd_scope = CpdScope.from_string(cpd_scope)
            except Exception as ex:
                raise OfCpdPathError(cpd_scope, reason = ex)

        # now it should be CpdScope
        validate_type(cpd_scope, "OF_CPD_SCOPE", CpdScope)
        return cpd_scope

    def store_results(
        self,
        outputs: Mapping[str, Any], # output name -> value
    ) -> DetailedResponse:
        """Store notebook's results."""
        validate_type(outputs, "outputs", abc.Mapping)
        for key, value in outputs.items():
            validate_type(key, f"outputs[...]", str)

        cpd_scope = self.get_scope_cpdpath() # needed for CPD variant anyway
        scope = self.get_scope(cpd_scope)

        storage_client: StorageClient

        if self.is_public:
            props = self._extract_storage_properties(scope)
            cos_config = StorageConfig.from_storage_properties(props)
            storage_client = CosClient(self, cos_config)
        else:
            guid = self._extract_storage_guid(scope)
            storage_client = CamsClient(self, cpd_scope, guid)

        output_artifacts = self.get_output_artifact_map()

        response = None
        for output_name, output_value in outputs.items():
            result_key = output_artifacts[output_name]
            response = storage_client.store_result(output_name, result_key, output_value)

        return response

@attrs(auto_attribs=True, frozen=True)
class WmlCredentialsAuth:
    def to_dict(self) -> dict:
        return attr.asdict(self)

@attrs(auto_attribs=True, frozen=True)
class WmlCredentialsApiKey(WmlCredentialsAuth):
    apikey: str

@attrs(auto_attribs=True, frozen=True)
class WmlCredentialsBearerToken(WmlCredentialsAuth):
    bearer_token: str

@attrs(auto_attribs=True, kw_only=True, frozen=True)
class WmlCredentials:
    guid: str
    name: str
    url: str
    auth: WmlCredentialsAuth

    def to_dict(self) -> dict:
        result = attr.asdict(self)

        # inline `auth` field
        auth = result['auth']
        del result['auth']
        result.update(auth)

        return result

@attrs(auto_attribs=True, kw_only=True, frozen=True)
class StorageCredentials:
    api_key: str
    service_id: str
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    resource_key_crn: Optional[str] = None

    def to_dict(self) -> dict:
        return attr.asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'StorageCredentials':
        fields = dict()
        for field_name, field in fields_dict(cls).items():
            field_required = field.default is NOTHING
            value = get_credentials_field(data, field_name, str, mandatory=field_required)
            if value is not None:
                fields[field_name] = value

        return cls(**fields)

@attrs(auto_attribs=True, kw_only=True, frozen=True)
class StorageCredentialsFull:
    admin: Optional[StorageCredentials] = None
    editor: Optional[StorageCredentials] = None
    viewer: StorageCredentials

    def to_dict(self) -> dict:
        return attr.asdict(self)

    @classmethod
    def from_storage_properties(cls, props: dict) -> 'StorageCredentialsFull':
        fields = dict()
        for field_name, field in fields_dict(cls).items():
            field_required = field.default is NOTHING
            path = "credentials." + field_name
            value = get_storage_config_field(props, path, dict, mandatory=field_required)
            if value is not None:
                fields[field_name] = StorageCredentials.from_dict(value)

        return cls(**fields)

@attrs(auto_attribs=True, kw_only=True, frozen=True)
class StorageConfig:
    DEFAULT_COS_AUTH_ENDPOINT: ClassVar[str] = 'https://iam.cloud.ibm.com/identity/token'

    endpoint: str
    api_key_id: str
    instance_crn: str
    auth_endpoint: str
    bucket_name: str

    @classmethod
    def from_storage_properties(cls, props: dict) -> 'StorageConfig':
        fields_to_paths = {
            "endpoint": "endpoint_url",
            "bucket_name": "bucket_name",
            "api_key_id": "credentials.editor.api_key",
            "instance_crn": "credentials.editor.resource_key_crn",
        }
        fields = dict()
        for field_name, field_path in fields_to_paths.items():
            fields[field_name] = get_storage_config_field(props, field_path, str)
        fields["auth_endpoint"] = cls._get_auth_endpoint_from_instance_crn(fields["instance_crn"])

        return cls(**fields)

    @classmethod
    def _get_auth_endpoint_from_instance_crn(cls, instance_crn: str) -> str:
        parts = instance_crn.split(":")
        cname = parts[2]
        cname_to_auth_endpoint = {
            'bluemix': 'https://iam.cloud.ibm.com/identity/token',
            'prod': 'https://iam.cloud.ibm.com/identity/token',
            'staging': 'https://iam.test.cloud.ibm.com/identity/token',
            'dev': 'https://iam.test.cloud.ibm.com/identity/token',
        }
        auth_endpoint = cname_to_auth_endpoint.get(cname, cls.DEFAULT_COS_AUTH_ENDPOINT)
        validate_type(auth_endpoint, "auth_endpoint", str)
        return auth_endpoint

class StorageClient(Protocol):
    @abstractmethod
    def store_result(self, output_name: str, output_key: str, value: Any) -> DetailedResponse: ...

class CosClient:
    def __init__(
        self,
        cpd_orchestration: WSPipelines,
        config: StorageConfig
    ):
        validate_type(cpd_orchestration, "cpd_orchestration", WSPipelines)
        validate_type(config, "config", StorageConfig)

        self.cpd_orchestration = cpd_orchestration
        self.config = config
        self.cos = ibm_boto3.resource(
            "s3",
            ibm_api_key_id=config.api_key_id,
            ibm_service_instance_id=config.instance_crn,
            ibm_auth_endpoint=config.auth_endpoint,
            config=Config(signature_version="oauth"),
            endpoint_url=config.endpoint
        )

    def store_result(self, output_name: str, output_key: str, value: Any) -> DetailedResponse:
        validate_type(output_name, "output_name", str)
        validate_type(output_key, "output_key", str)

        if isinstance(value, io.TextIOBase):
            # not supported yet
            raise FilesResultsNotSupportedError(output_name)
        else:
            value = str(value)

        cos_response = self.cos.Object(self.config.bucket_name, output_key).put(
            Body=value
        )
        response = requests.Response()
        response.request = requests.Request(
            method = 'PUT',
            url = urljoin(urljoin(self.config.endpoint, self.config.bucket_name), output_key),
            headers = {},
        )
        response.status_code = cos_response['ResponseMetadata']['HTTPStatusCode']
        response.headers = cos_response['ResponseMetadata']['HTTPHeaders']
        return DetailedResponse(
            response=response
        )

class CamsClient:
    def __init__(
        self,
        cpd_orchestration: WSPipelines,
        scope: CpdScope,
        guid: str,
    ):
        validate_type(cpd_orchestration, "cpd_orchestration", WSPipelines)
        validate_type(scope, "scope", CpdScope)
        validate_type(guid, "guid", str)

        self.cpd_orchestration = cpd_orchestration
        self.scope = scope
        self.guid = guid

    def store_result(self, output_name: str, output_key: str, value: Any) -> DetailedResponse:
        validate_type(output_name, "output_name", str)
        validate_type(output_key, "output_key", str)

        if isinstance(value, io.TextIOBase):
            # not supported yet
            raise FilesResultsNotSupportedError(output_name)
        else:
            value = str(value)

        scope_key = self.scope.scope_type()
        if scope_key.endswith('s'):
            scope_key = scope_key[:-1]
        scope_key += '_id'

        headers = {
            "Accept": "application/json",
        }
        params = {
            scope_key: self.scope.scope_id(),
        }

        if self.scope.context is not None and self.scope.context != '':
            params["context"] = self.scope.context

        asset_uri_prefix = '/v2/asset_files/'
        asset_file_uri = quote(output_key, safe='')
        uri = urljoin(asset_uri_prefix, asset_file_uri)

        files = {
            "file": (output_key.split('/')[-1], value)
        }

        req = self.cpd_orchestration.prepare_request('PUT', uri, headers=headers, params=params, files=files)
        req = cast(requests.Request, req)
        res = self.cpd_orchestration.send(req)
        return res