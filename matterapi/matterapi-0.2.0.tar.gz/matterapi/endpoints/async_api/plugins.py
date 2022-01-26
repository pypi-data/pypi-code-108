from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ...models import (
    GetPluginsResponse_200,
    InstallMarketplacePluginJsonBody,
    MarketplacePlugin,
    PluginManifest,
    PluginManifestWebapp,
    PluginStatus,
    StatusOK,
    System,
    UploadPluginMultipartData,
)
from ..base import ApiBaseClass


class PluginsApi(ApiBaseClass):
    """Endpoints related to uploading and managing plugins."""

    async def get_plugins(
        self,
    ) -> GetPluginsResponse_200:
        """Get plugins

        Get a list of inactive and a list of active plugin manifests. Plugins
        must be enabled in the server's config settings.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            4.4
        """

        url = "/plugins".format()

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = GetPluginsResponse_200.parse_obj(response.json())

            return response_200
        return response

    async def upload_plugin(
        self,
        *,
        multipart_data: UploadPluginMultipartData,
    ) -> StatusOK:
        """Upload plugin

        Upload a plugin that is contained within a compressed .tar.gz file.
        Plugins and plugin uploads must be enabled in the server's config
        settings.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            4.4
        """

        url = "/plugins".format()

        multipart_body_data = UploadPluginMultipartData.parse_obj(multipart_data)

        request_kwargs = {
            "url": url,
            "data": multipart_body_data.get_data(),
            "files": multipart_body_data.get_files(),
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = StatusOK.parse_obj(response.json())

            return response_201
        return response

    async def install_plugin_from_url(
        self,
        *,
        plugin_download_url: str,
        force: Optional[str] = None,
    ) -> StatusOK:
        """Install plugin from url

        Supply a URL to a plugin compressed in a .tar.gz file. Plugins must be
        enabled in the server's config settings.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.14
        """

        url = "/plugins/install_from_url".format()
        params: Dict[str, Any] = {
            "plugin_download_url": plugin_download_url,
            "force": force,
        }
        params = {k: v for k, v in params.items() if v is not None}

        request_kwargs = {
            "url": url,
            "params": params,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = StatusOK.parse_obj(response.json())

            return response_201
        return response

    async def remove_plugin(
        self,
        plugin_id: str,
    ) -> StatusOK:
        """Remove plugin

        Remove the plugin with the provided ID from the server. All plugin files
        are deleted. Plugins must be enabled in the server's config settings.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            4.4
        """

        url = "/plugins/{plugin_id}".format(
            plugin_id=plugin_id,
        )

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.delete(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def enable_plugin(
        self,
        plugin_id: str,
    ) -> StatusOK:
        """Enable plugin

        Enable a previously uploaded plugin. Plugins must be enabled in the
        server's config settings.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            4.4
        """

        url = "/plugins/{plugin_id}/enable".format(
            plugin_id=plugin_id,
        )

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def disable_plugin(
        self,
        plugin_id: str,
    ) -> StatusOK:
        """Disable plugin

        Disable a previously enabled plugin. Plugins must be enabled in the
        server's config settings.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            4.4
        """

        url = "/plugins/{plugin_id}/disable".format(
            plugin_id=plugin_id,
        )

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def get_webapp_plugins(
        self,
    ) -> List[PluginManifestWebapp]:
        """Get webapp plugins

        Get a list of web app plugins installed and activated on the server.

        Permissions:
            No permissions required.
        Minimum Server Version:
            4.4
        """

        url = "/plugins/webapp".format()

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = PluginManifestWebapp.parse_obj(
                    response_200_item_data
                )

                response_200.append(response_200_item)

            return response_200
        return response

    async def get_plugin_statuses(
        self,
    ) -> List[PluginStatus]:
        """Get plugins status

        Returns the status for plugins installed anywhere in the cluster

        Permissions:
            No permissions required.
        Minimum Server Version:
            4.4
        """

        url = "/plugins/statuses".format()

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = PluginStatus.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    async def get_marketplace_plugins(
        self,
        *,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        filter: Optional[str] = None,
        server_version: Optional[str] = None,
        local_only: Optional[bool] = None,
    ) -> List[MarketplacePlugin]:
        """Gets all the marketplace plugins

        Gets all plugins from the marketplace server, merging data from locally
        installed plugins as well as prepackaged plugins shipped with the
        server.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.16
        """

        url = "/plugins/marketplace".format()
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "filter": filter,
            "server_version": server_version,
            "local_only": local_only,
        }
        params = {k: v for k, v in params.items() if v is not None}

        request_kwargs = {
            "url": url,
            "params": params,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = MarketplacePlugin.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    async def install_marketplace_plugin(
        self,
        *,
        json_body: InstallMarketplacePluginJsonBody,
    ) -> PluginManifest:
        """Installs a marketplace plugin

        Installs a plugin listed in the marketplace server.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.16
        """

        url = "/plugins/marketplace".format()

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = PluginManifest.parse_obj(response.json())

            return response_200
        return response

    async def get_marketplace_visited_by_admin(
        self,
    ) -> System:
        """Get if the Plugin Marketplace has been visited by at least an admin.

        Retrieves the status that specifies that at least one System Admin has
        visited the in-product Plugin Marketplace.

        Permissions:
            Must have `manage_system` permissions.
        Minimum Server Version:
            5.33
        """

        url = "/plugins/marketplace/first_admin_visit".format()

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = System.parse_obj(response.json())

            return response_200
        return response
