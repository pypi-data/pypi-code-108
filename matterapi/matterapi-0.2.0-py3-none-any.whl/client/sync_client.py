from contextlib import contextmanager
from typing import Optional

import httpx
from pydantic import PrivateAttr

from ..endpoints.sync_api.authentication import AuthenticationApi
from ..endpoints.sync_api.bleve import BleveApi
from ..endpoints.sync_api.bots import BotsApi
from ..endpoints.sync_api.brand import BrandApi
from ..endpoints.sync_api.channels import ChannelsApi
from ..endpoints.sync_api.cloud import CloudApi
from ..endpoints.sync_api.cluster import ClusterApi
from ..endpoints.sync_api.commands import CommandsApi
from ..endpoints.sync_api.compliance import ComplianceApi
from ..endpoints.sync_api.data_retention import DataRetentionApi
from ..endpoints.sync_api.elasticsearch import ElasticsearchApi
from ..endpoints.sync_api.emoji import EmojiApi
from ..endpoints.sync_api.exports import ExportsApi
from ..endpoints.sync_api.files import FilesApi
from ..endpoints.sync_api.groups import GroupsApi
from ..endpoints.sync_api.imports import ImportsApi
from ..endpoints.sync_api.integration_actions import IntegrationActionsApi
from ..endpoints.sync_api.jobs import JobsApi
from ..endpoints.sync_api.ldap import LdapApi
from ..endpoints.sync_api.migrate import MigrateApi
from ..endpoints.sync_api.oauth import OauthApi
from ..endpoints.sync_api.open_graph import OpenGraphApi
from ..endpoints.sync_api.permissions import PermissionsApi
from ..endpoints.sync_api.plugins import PluginsApi
from ..endpoints.sync_api.posts import PostsApi
from ..endpoints.sync_api.preferences import PreferencesApi
from ..endpoints.sync_api.reactions import ReactionsApi
from ..endpoints.sync_api.roles import RolesApi
from ..endpoints.sync_api.root import RootApi
from ..endpoints.sync_api.saml import SamlApi
from ..endpoints.sync_api.schemes import SchemesApi
from ..endpoints.sync_api.search import SearchApi
from ..endpoints.sync_api.shared_channels import SharedChannelsApi
from ..endpoints.sync_api.status import StatusApi
from ..endpoints.sync_api.system import SystemApi
from ..endpoints.sync_api.teams import TeamsApi
from ..endpoints.sync_api.terms_of_service import TermsOfServiceApi
from ..endpoints.sync_api.threads import ThreadsApi
from ..endpoints.sync_api.uploads import UploadsApi
from ..endpoints.sync_api.users import UsersApi
from ..endpoints.sync_api.webhooks import WebhooksApi
from .base import AuthLogin, AuthToken, BaseClient, HttpxClientOptions
from .exceptions import (
    ContentTooLarge,
    FeatureDisabled,
    InternalServerError,
    InvalidOrMissingParameters,
    MethodNotAllowed,
    NoAccessTokenProvided,
    NotEnoughPermissions,
    ResourceNotFound,
    TooManyRequests,
)


class SyncClient(BaseClient):
    """Synchronous mattermost api client implementation"""

    _httpx_client: Optional[httpx.Client] = PrivateAttr(None)
    """ The underlying httpx client which handles requests to the api in case we are inside a session """

    def _create_httpx_client(self):
        """Create a httpx.Client instance to be used for requests and perform authentication if needed"""
        httpx_client_options = (
            self.options.httpx_client_options
            if self.options.httpx_client_options
            else HttpxClientOptions()
        )
        base_url = str(httpx.URL(self.options.url).join(self.options.basepath))
        httpx_client = httpx.Client(base_url=base_url, **dict(httpx_client_options))
        httpx_client.event_hooks["response"] = [
            self.raise_on_4xx_5xx
        ] + httpx_client.event_hooks["response"]
        if isinstance(self.options.auth, AuthToken):
            httpx_client.auth = self.options.auth
            self.active_token = self.options.auth.token
        if isinstance(self.options.auth, AuthLogin):
            """Login with username and password and get a session_token"""
            response = httpx_client.post(
                url="/users/login", json=self.options.auth.dict(exclude_unset=True)
            )
            session_token = response.headers.get("token", None)
            httpx_client.auth = AuthToken(token=session_token)
            self.active_token = session_token
        return httpx_client

    def raise_on_4xx_5xx(self, response):
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            try:
                e.response.read()
                data = e.response.json()
                message = data.get("message", data)
            except ValueError:
                message = response.text
            if e.response.status_code == 400:
                raise InvalidOrMissingParameters(message) from e
            if e.response.status_code == 401:
                raise NoAccessTokenProvided(message) from e
            if e.response.status_code == 403:
                raise NotEnoughPermissions(message) from e
            if e.response.status_code == 404:
                raise ResourceNotFound(message) from e
            if e.response.status_code == 405:
                raise MethodNotAllowed(message) from e
            if e.response.status_code == 413:
                raise ContentTooLarge(message) from e
            if e.response.status_code == 429:
                raise TooManyRequests(message) from e
            if e.response.status_code == 500:
                raise InternalServerError(message) from e
            if e.response.status_code == 501:
                raise FeatureDisabled(message) from e
            raise

    def _login(self):
        """Calling this creates a httpx client and sets .active_token, needed for websockets"""
        self._create_httpx_client()

    @contextmanager
    def _get_httpx_client(self):
        """Get the currently set httpx.Client instance or create a new one"""
        if not self._httpx_client or self._httpx_client.is_closed:
            httpx_client = self._create_httpx_client()
            try:
                yield httpx_client
            finally:
                httpx_client.close()
        else:
            yield self._httpx_client

    @contextmanager
    def session(self):
        """Open a Session which re-uses the underlying httpx client and it's connections"""
        api_client = self.copy()
        api_client._httpx_client = api_client._create_httpx_client()
        try:
            yield api_client
        finally:
            api_client._httpx_client.close()

    @property
    def users(self) -> UsersApi:
        """Api endpoint for Users

        :type: :class:`~matterapi.endpoints.sync_api.UsersApi`
        """
        return UsersApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def bots(self) -> BotsApi:
        """Api endpoint for Bots

        :type: :class:`~matterapi.endpoints.sync_api.BotsApi`
        """
        return BotsApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def terms_of_service(self) -> TermsOfServiceApi:
        """Api endpoint for TermsOfService

        :type: :class:`~matterapi.endpoints.sync_api.TermsOfServiceApi`
        """
        return TermsOfServiceApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def migrate(self) -> MigrateApi:
        """Api endpoint for Migrate

        :type: :class:`~matterapi.endpoints.sync_api.MigrateApi`
        """
        return MigrateApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def authentication(self) -> AuthenticationApi:
        """Api endpoint for Authentication

        :type: :class:`~matterapi.endpoints.sync_api.AuthenticationApi`
        """
        return AuthenticationApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def ldap(self) -> LdapApi:
        """Api endpoint for Ldap

        :type: :class:`~matterapi.endpoints.sync_api.LdapApi`
        """
        return LdapApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def saml(self) -> SamlApi:
        """Api endpoint for Saml

        :type: :class:`~matterapi.endpoints.sync_api.SamlApi`
        """
        return SamlApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def threads(self) -> ThreadsApi:
        """Api endpoint for Threads

        :type: :class:`~matterapi.endpoints.sync_api.ThreadsApi`
        """
        return ThreadsApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def data_retention(self) -> DataRetentionApi:
        """Api endpoint for DataRetention

        :type: :class:`~matterapi.endpoints.sync_api.DataRetentionApi`
        """
        return DataRetentionApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def status(self) -> StatusApi:
        """Api endpoint for Status

        :type: :class:`~matterapi.endpoints.sync_api.StatusApi`
        """
        return StatusApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def teams(self) -> TeamsApi:
        """Api endpoint for Teams

        :type: :class:`~matterapi.endpoints.sync_api.TeamsApi`
        """
        return TeamsApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def channels(self) -> ChannelsApi:
        """Api endpoint for Channels

        :type: :class:`~matterapi.endpoints.sync_api.ChannelsApi`
        """
        return ChannelsApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def posts(self) -> PostsApi:
        """Api endpoint for Posts

        :type: :class:`~matterapi.endpoints.sync_api.PostsApi`
        """
        return PostsApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def preferences(self) -> PreferencesApi:
        """Api endpoint for Preferences

        :type: :class:`~matterapi.endpoints.sync_api.PreferencesApi`
        """
        return PreferencesApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def files(self) -> FilesApi:
        """Api endpoint for Files

        :type: :class:`~matterapi.endpoints.sync_api.FilesApi`
        """
        return FilesApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def search(self) -> SearchApi:
        """Api endpoint for Search

        :type: :class:`~matterapi.endpoints.sync_api.SearchApi`
        """
        return SearchApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def uploads(self) -> UploadsApi:
        """Api endpoint for Uploads

        :type: :class:`~matterapi.endpoints.sync_api.UploadsApi`
        """
        return UploadsApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def jobs(self) -> JobsApi:
        """Api endpoint for Jobs

        :type: :class:`~matterapi.endpoints.sync_api.JobsApi`
        """
        return JobsApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def system(self) -> SystemApi:
        """Api endpoint for System

        :type: :class:`~matterapi.endpoints.sync_api.SystemApi`
        """
        return SystemApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def root(self) -> RootApi:
        """Api endpoint for Root

        :type: :class:`~matterapi.endpoints.sync_api.RootApi`
        """
        return RootApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def emoji(self) -> EmojiApi:
        """Api endpoint for Emoji

        :type: :class:`~matterapi.endpoints.sync_api.EmojiApi`
        """
        return EmojiApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def webhooks(self) -> WebhooksApi:
        """Api endpoint for Webhooks

        :type: :class:`~matterapi.endpoints.sync_api.WebhooksApi`
        """
        return WebhooksApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def compliance(self) -> ComplianceApi:
        """Api endpoint for Compliance

        :type: :class:`~matterapi.endpoints.sync_api.ComplianceApi`
        """
        return ComplianceApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def groups(self) -> GroupsApi:
        """Api endpoint for Groups

        :type: :class:`~matterapi.endpoints.sync_api.GroupsApi`
        """
        return GroupsApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def cluster(self) -> ClusterApi:
        """Api endpoint for Cluster

        :type: :class:`~matterapi.endpoints.sync_api.ClusterApi`
        """
        return ClusterApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def brand(self) -> BrandApi:
        """Api endpoint for Brand

        :type: :class:`~matterapi.endpoints.sync_api.BrandApi`
        """
        return BrandApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def commands(self) -> CommandsApi:
        """Api endpoint for Commands

        :type: :class:`~matterapi.endpoints.sync_api.CommandsApi`
        """
        return CommandsApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def oauth(self) -> OauthApi:
        """Api endpoint for Oauth

        :type: :class:`~matterapi.endpoints.sync_api.OauthApi`
        """
        return OauthApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def elasticsearch(self) -> ElasticsearchApi:
        """Api endpoint for Elasticsearch

        :type: :class:`~matterapi.endpoints.sync_api.ElasticsearchApi`
        """
        return ElasticsearchApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def bleve(self) -> BleveApi:
        """Api endpoint for Bleve

        :type: :class:`~matterapi.endpoints.sync_api.BleveApi`
        """
        return BleveApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def plugins(self) -> PluginsApi:
        """Api endpoint for Plugins

        :type: :class:`~matterapi.endpoints.sync_api.PluginsApi`
        """
        return PluginsApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def roles(self) -> RolesApi:
        """Api endpoint for Roles

        :type: :class:`~matterapi.endpoints.sync_api.RolesApi`
        """
        return RolesApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def schemes(self) -> SchemesApi:
        """Api endpoint for Schemes

        :type: :class:`~matterapi.endpoints.sync_api.SchemesApi`
        """
        return SchemesApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def shared_channels(self) -> SharedChannelsApi:
        """Api endpoint for SharedChannels

        :type: :class:`~matterapi.endpoints.sync_api.SharedChannelsApi`
        """
        return SharedChannelsApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def open_graph(self) -> OpenGraphApi:
        """Api endpoint for OpenGraph

        :type: :class:`~matterapi.endpoints.sync_api.OpenGraphApi`
        """
        return OpenGraphApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def reactions(self) -> ReactionsApi:
        """Api endpoint for Reactions

        :type: :class:`~matterapi.endpoints.sync_api.ReactionsApi`
        """
        return ReactionsApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def integration_actions(self) -> IntegrationActionsApi:
        """Api endpoint for IntegrationActions

        :type: :class:`~matterapi.endpoints.sync_api.IntegrationActionsApi`
        """
        return IntegrationActionsApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def cloud(self) -> CloudApi:
        """Api endpoint for Cloud

        :type: :class:`~matterapi.endpoints.sync_api.CloudApi`
        """
        return CloudApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def permissions(self) -> PermissionsApi:
        """Api endpoint for Permissions

        :type: :class:`~matterapi.endpoints.sync_api.PermissionsApi`
        """
        return PermissionsApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def imports(self) -> ImportsApi:
        """Api endpoint for Imports

        :type: :class:`~matterapi.endpoints.sync_api.ImportsApi`
        """
        return ImportsApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )

    @property
    def exports(self) -> ExportsApi:
        """Api endpoint for Exports

        :type: :class:`~matterapi.endpoints.sync_api.ExportsApi`
        """
        return ExportsApi(
            client=self, skip_response_parsing=self.options.skip_response_parsing
        )
