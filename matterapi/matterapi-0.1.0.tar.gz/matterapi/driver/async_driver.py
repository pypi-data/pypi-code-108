from typing import Optional, Union

import httpx
from pydantic import PrivateAttr

from ..endpoints.async_api.authentication import AuthenticationApi
from ..endpoints.async_api.bleve import BleveApi
from ..endpoints.async_api.bots import BotsApi
from ..endpoints.async_api.brand import BrandApi
from ..endpoints.async_api.channels import ChannelsApi
from ..endpoints.async_api.cloud import CloudApi
from ..endpoints.async_api.cluster import ClusterApi
from ..endpoints.async_api.commands import CommandsApi
from ..endpoints.async_api.compliance import ComplianceApi
from ..endpoints.async_api.data_retention import DataRetentionApi
from ..endpoints.async_api.elasticsearch import ElasticsearchApi
from ..endpoints.async_api.emoji import EmojiApi
from ..endpoints.async_api.exports import ExportsApi
from ..endpoints.async_api.files import FilesApi
from ..endpoints.async_api.groups import GroupsApi
from ..endpoints.async_api.imports import ImportsApi
from ..endpoints.async_api.integration_actions import IntegrationActionsApi
from ..endpoints.async_api.jobs import JobsApi
from ..endpoints.async_api.ldap import LdapApi
from ..endpoints.async_api.migrate import MigrateApi
from ..endpoints.async_api.oauth import OauthApi
from ..endpoints.async_api.open_graph import OpenGraphApi
from ..endpoints.async_api.permissions import PermissionsApi
from ..endpoints.async_api.plugins import PluginsApi
from ..endpoints.async_api.posts import PostsApi
from ..endpoints.async_api.preferences import PreferencesApi
from ..endpoints.async_api.reactions import ReactionsApi
from ..endpoints.async_api.roles import RolesApi
from ..endpoints.async_api.root import RootApi
from ..endpoints.async_api.saml import SamlApi
from ..endpoints.async_api.schemes import SchemesApi
from ..endpoints.async_api.search import SearchApi
from ..endpoints.async_api.shared_channels import SharedChannelsApi
from ..endpoints.async_api.status import StatusApi
from ..endpoints.async_api.system import SystemApi
from ..endpoints.async_api.teams import TeamsApi
from ..endpoints.async_api.terms_of_service import TermsOfServiceApi
from ..endpoints.async_api.threads import ThreadsApi
from ..endpoints.async_api.uploads import UploadsApi
from ..endpoints.async_api.users import UsersApi
from ..endpoints.async_api.webhooks import WebhooksApi
from ..models import User
from .base import AuthLogin, AuthToken, BaseDriver
from .client import AsyncAuthenticatedClient, AsyncClient
from .exceptions import ApiError


class AsyncDriver(BaseDriver):
    """Asynchronous mattermost api driver implementation"""

    _client: Optional[Union[AsyncClient, AsyncAuthenticatedClient]] = PrivateAttr(None)
    """ The underlying Client which handles requests to the api """

    async def login(self):
        """
        Login with the provided authentication information.
        """
        url = str(httpx.URL(self.options.url).join(self.options.basepath))
        self._client = self._client or AsyncClient(
            base_url=url, client_options=self.options.client_options
        )

        if isinstance(self.options.auth, AuthToken):
            self.active_token = self.options.auth.token
            self._client = AsyncAuthenticatedClient(
                base_url=url,
                auth_token=self.options.auth.token,
                client_options=self.options.client_options,
            )
            user_api = UsersApi(self._client)
            self.user = await user_api.get_user("me")
        elif isinstance(self.options.auth, AuthLogin):
            user_api = UsersApi(self._client)
            response = await user_api.login(json_body=self.options.auth)
            self.user = User.parse_obj(response.json())
            session_token = response.headers["token"]
            self.active_token = session_token
            self._client = AsyncAuthenticatedClient(
                base_url=url,
                auth_token=session_token,
                client_options=self.options.client_options,
            )
        else:
            raise ApiError("No valid authentication credentials provided")

    @property
    def users(self) -> UsersApi:
        """Api endpoint for Users

        :type: :class:`~matterapi.endpoints.async_api.UsersApi`
        """
        return UsersApi(self._client, self.options.skip_response_parsing)

    @property
    def bots(self) -> BotsApi:
        """Api endpoint for Bots

        :type: :class:`~matterapi.endpoints.async_api.BotsApi`
        """
        return BotsApi(self._client, self.options.skip_response_parsing)

    @property
    def terms_of_service(self) -> TermsOfServiceApi:
        """Api endpoint for TermsOfService

        :type: :class:`~matterapi.endpoints.async_api.TermsOfServiceApi`
        """
        return TermsOfServiceApi(self._client, self.options.skip_response_parsing)

    @property
    def migrate(self) -> MigrateApi:
        """Api endpoint for Migrate

        :type: :class:`~matterapi.endpoints.async_api.MigrateApi`
        """
        return MigrateApi(self._client, self.options.skip_response_parsing)

    @property
    def authentication(self) -> AuthenticationApi:
        """Api endpoint for Authentication

        :type: :class:`~matterapi.endpoints.async_api.AuthenticationApi`
        """
        return AuthenticationApi(self._client, self.options.skip_response_parsing)

    @property
    def ldap(self) -> LdapApi:
        """Api endpoint for Ldap

        :type: :class:`~matterapi.endpoints.async_api.LdapApi`
        """
        return LdapApi(self._client, self.options.skip_response_parsing)

    @property
    def saml(self) -> SamlApi:
        """Api endpoint for Saml

        :type: :class:`~matterapi.endpoints.async_api.SamlApi`
        """
        return SamlApi(self._client, self.options.skip_response_parsing)

    @property
    def threads(self) -> ThreadsApi:
        """Api endpoint for Threads

        :type: :class:`~matterapi.endpoints.async_api.ThreadsApi`
        """
        return ThreadsApi(self._client, self.options.skip_response_parsing)

    @property
    def data_retention(self) -> DataRetentionApi:
        """Api endpoint for DataRetention

        :type: :class:`~matterapi.endpoints.async_api.DataRetentionApi`
        """
        return DataRetentionApi(self._client, self.options.skip_response_parsing)

    @property
    def status(self) -> StatusApi:
        """Api endpoint for Status

        :type: :class:`~matterapi.endpoints.async_api.StatusApi`
        """
        return StatusApi(self._client, self.options.skip_response_parsing)

    @property
    def teams(self) -> TeamsApi:
        """Api endpoint for Teams

        :type: :class:`~matterapi.endpoints.async_api.TeamsApi`
        """
        return TeamsApi(self._client, self.options.skip_response_parsing)

    @property
    def channels(self) -> ChannelsApi:
        """Api endpoint for Channels

        :type: :class:`~matterapi.endpoints.async_api.ChannelsApi`
        """
        return ChannelsApi(self._client, self.options.skip_response_parsing)

    @property
    def posts(self) -> PostsApi:
        """Api endpoint for Posts

        :type: :class:`~matterapi.endpoints.async_api.PostsApi`
        """
        return PostsApi(self._client, self.options.skip_response_parsing)

    @property
    def preferences(self) -> PreferencesApi:
        """Api endpoint for Preferences

        :type: :class:`~matterapi.endpoints.async_api.PreferencesApi`
        """
        return PreferencesApi(self._client, self.options.skip_response_parsing)

    @property
    def files(self) -> FilesApi:
        """Api endpoint for Files

        :type: :class:`~matterapi.endpoints.async_api.FilesApi`
        """
        return FilesApi(self._client, self.options.skip_response_parsing)

    @property
    def search(self) -> SearchApi:
        """Api endpoint for Search

        :type: :class:`~matterapi.endpoints.async_api.SearchApi`
        """
        return SearchApi(self._client, self.options.skip_response_parsing)

    @property
    def uploads(self) -> UploadsApi:
        """Api endpoint for Uploads

        :type: :class:`~matterapi.endpoints.async_api.UploadsApi`
        """
        return UploadsApi(self._client, self.options.skip_response_parsing)

    @property
    def jobs(self) -> JobsApi:
        """Api endpoint for Jobs

        :type: :class:`~matterapi.endpoints.async_api.JobsApi`
        """
        return JobsApi(self._client, self.options.skip_response_parsing)

    @property
    def system(self) -> SystemApi:
        """Api endpoint for System

        :type: :class:`~matterapi.endpoints.async_api.SystemApi`
        """
        return SystemApi(self._client, self.options.skip_response_parsing)

    @property
    def root(self) -> RootApi:
        """Api endpoint for Root

        :type: :class:`~matterapi.endpoints.async_api.RootApi`
        """
        return RootApi(self._client, self.options.skip_response_parsing)

    @property
    def emoji(self) -> EmojiApi:
        """Api endpoint for Emoji

        :type: :class:`~matterapi.endpoints.async_api.EmojiApi`
        """
        return EmojiApi(self._client, self.options.skip_response_parsing)

    @property
    def webhooks(self) -> WebhooksApi:
        """Api endpoint for Webhooks

        :type: :class:`~matterapi.endpoints.async_api.WebhooksApi`
        """
        return WebhooksApi(self._client, self.options.skip_response_parsing)

    @property
    def compliance(self) -> ComplianceApi:
        """Api endpoint for Compliance

        :type: :class:`~matterapi.endpoints.async_api.ComplianceApi`
        """
        return ComplianceApi(self._client, self.options.skip_response_parsing)

    @property
    def groups(self) -> GroupsApi:
        """Api endpoint for Groups

        :type: :class:`~matterapi.endpoints.async_api.GroupsApi`
        """
        return GroupsApi(self._client, self.options.skip_response_parsing)

    @property
    def cluster(self) -> ClusterApi:
        """Api endpoint for Cluster

        :type: :class:`~matterapi.endpoints.async_api.ClusterApi`
        """
        return ClusterApi(self._client, self.options.skip_response_parsing)

    @property
    def brand(self) -> BrandApi:
        """Api endpoint for Brand

        :type: :class:`~matterapi.endpoints.async_api.BrandApi`
        """
        return BrandApi(self._client, self.options.skip_response_parsing)

    @property
    def commands(self) -> CommandsApi:
        """Api endpoint for Commands

        :type: :class:`~matterapi.endpoints.async_api.CommandsApi`
        """
        return CommandsApi(self._client, self.options.skip_response_parsing)

    @property
    def oauth(self) -> OauthApi:
        """Api endpoint for Oauth

        :type: :class:`~matterapi.endpoints.async_api.OauthApi`
        """
        return OauthApi(self._client, self.options.skip_response_parsing)

    @property
    def elasticsearch(self) -> ElasticsearchApi:
        """Api endpoint for Elasticsearch

        :type: :class:`~matterapi.endpoints.async_api.ElasticsearchApi`
        """
        return ElasticsearchApi(self._client, self.options.skip_response_parsing)

    @property
    def bleve(self) -> BleveApi:
        """Api endpoint for Bleve

        :type: :class:`~matterapi.endpoints.async_api.BleveApi`
        """
        return BleveApi(self._client, self.options.skip_response_parsing)

    @property
    def plugins(self) -> PluginsApi:
        """Api endpoint for Plugins

        :type: :class:`~matterapi.endpoints.async_api.PluginsApi`
        """
        return PluginsApi(self._client, self.options.skip_response_parsing)

    @property
    def roles(self) -> RolesApi:
        """Api endpoint for Roles

        :type: :class:`~matterapi.endpoints.async_api.RolesApi`
        """
        return RolesApi(self._client, self.options.skip_response_parsing)

    @property
    def schemes(self) -> SchemesApi:
        """Api endpoint for Schemes

        :type: :class:`~matterapi.endpoints.async_api.SchemesApi`
        """
        return SchemesApi(self._client, self.options.skip_response_parsing)

    @property
    def shared_channels(self) -> SharedChannelsApi:
        """Api endpoint for SharedChannels

        :type: :class:`~matterapi.endpoints.async_api.SharedChannelsApi`
        """
        return SharedChannelsApi(self._client, self.options.skip_response_parsing)

    @property
    def open_graph(self) -> OpenGraphApi:
        """Api endpoint for OpenGraph

        :type: :class:`~matterapi.endpoints.async_api.OpenGraphApi`
        """
        return OpenGraphApi(self._client, self.options.skip_response_parsing)

    @property
    def reactions(self) -> ReactionsApi:
        """Api endpoint for Reactions

        :type: :class:`~matterapi.endpoints.async_api.ReactionsApi`
        """
        return ReactionsApi(self._client, self.options.skip_response_parsing)

    @property
    def integration_actions(self) -> IntegrationActionsApi:
        """Api endpoint for IntegrationActions

        :type: :class:`~matterapi.endpoints.async_api.IntegrationActionsApi`
        """
        return IntegrationActionsApi(self._client, self.options.skip_response_parsing)

    @property
    def cloud(self) -> CloudApi:
        """Api endpoint for Cloud

        :type: :class:`~matterapi.endpoints.async_api.CloudApi`
        """
        return CloudApi(self._client, self.options.skip_response_parsing)

    @property
    def permissions(self) -> PermissionsApi:
        """Api endpoint for Permissions

        :type: :class:`~matterapi.endpoints.async_api.PermissionsApi`
        """
        return PermissionsApi(self._client, self.options.skip_response_parsing)

    @property
    def imports(self) -> ImportsApi:
        """Api endpoint for Imports

        :type: :class:`~matterapi.endpoints.async_api.ImportsApi`
        """
        return ImportsApi(self._client, self.options.skip_response_parsing)

    @property
    def exports(self) -> ExportsApi:
        """Api endpoint for Exports

        :type: :class:`~matterapi.endpoints.async_api.ExportsApi`
        """
        return ExportsApi(self._client, self.options.skip_response_parsing)
