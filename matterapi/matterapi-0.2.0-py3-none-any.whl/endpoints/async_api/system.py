from typing import Any, Dict, List, Optional, cast

from pydantic import BaseModel

from ...models import (
    Audit,
    Config,
    EnvironmentConfig,
    IntegrityCheckResult,
    LicenseRenewalLink,
    MigrateConfigJsonBody,
    Notice,
    PostLogJsonBody,
    PostLogResponse_200,
    PushNotification,
    RequestTrialLicenseJsonBody,
    SendWarnMetricAckJsonBody,
    Server_Busy,
    StatusOK,
    System,
    SystemStatusResponse,
    TestSiteURLJsonBody,
    UpgradeToEnterpriseStatusResponse_200,
    UploadLicenseFileMultipartData,
)
from ..base import ApiBaseClass


class SystemApi(ApiBaseClass):
    """General endpoints for interacting with the server, such as configuration
    and logging."""

    async def get_supported_timezone(
        self,
    ) -> List[str]:
        """Retrieve a list of supported timezones



        Permissions:
            Must be logged in.
        Minimum Server Version:
            3.10
        """

        url = "/system/timezones".format()

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
            response_200 = cast(List[str], response.json())

            return response_200
        return response

    async def get_ping(
        self,
        *,
        get_server_status: Optional[bool] = None,
    ) -> SystemStatusResponse:
        """Check system health

        Check if the server is up and healthy based on the configuration setting
        `GoRoutineHealthThreshold`. If `GoRoutineHealthThreshold` and the number
        of goroutines on the server exceeds that threshold the server is
        considered unhealthy. If `GoRoutineHealthThreshold` is not set or the
        number of goroutines is below the threshold the server is considered
        healthy.

        Permissions:
            Must be logged in.
        Minimum Server Version:
            3.10
        """

        url = "/system/ping".format()
        params: Dict[str, Any] = {
            "get_server_status": get_server_status,
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
            response_200 = SystemStatusResponse.parse_obj(response.json())

            return response_200
        return response

    async def get_notices(
        self,
        team_id: str,
        *,
        client_version: str,
        locale: Optional[str] = None,
        client: str,
    ) -> List[Notice]:
        """Get notices for logged in user in specified team

        Will return appropriate product notices for current user in the team
        specified by teamId parameter.

        Permissions:
            Must be logged in.
        Minimum Server Version:
            5.26
        """

        url = "/system/notices/{teamId}".format(
            teamId=team_id,
        )
        params: Dict[str, Any] = {
            "clientVersion": client_version,
            "locale": locale,
            "client": client,
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
                response_200_item = Notice.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    async def mark_notices_viewed(
        self,
        *,
        json_body: List[str],
    ) -> StatusOK:
        """Update notices as 'viewed'

        Will mark the specified notices as 'viewed' by the logged in user.

        Permissions:
            Must be logged in.
        Minimum Server Version:
            5.26
        """

        url = "/system/notices/view".format()
        json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.put(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def database_recycle(
        self,
    ) -> StatusOK:
        """Recycle database connections

        Recycle database connections by closing and reconnecting all connections
        to master and read replica databases.

        Permissions:
            Must have `manage_system` permission.
        """

        url = "/database/recycle".format()

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

    async def test_email(
        self,
        *,
        json_body: Config,
    ) -> StatusOK:
        """Send a test email

        Send a test email to make sure you have your email settings configured
        correctly. Optionally provide a configuration in the request body to
        test. If no valid configuration is present in the request body the
        current server configuration will be tested.

        Permissions:
            Must have `manage_system` permission.
        """

        url = "/email/test".format()

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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def test_site_url(
        self,
        *,
        json_body: TestSiteURLJsonBody,
    ) -> StatusOK:
        """Checks the validity of a Site URL

        Sends a Ping request to the mattermost server using the specified Site
        URL.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.16
        """

        url = "/site_url/test".format()

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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def test_s3_connection(
        self,
        *,
        json_body: Config,
    ) -> StatusOK:
        """Test AWS S3 connection

        Send a test to validate if can connect to AWS S3. Optionally provide a
        configuration in the request body to test. If no valid configuration is
        present in the request body the current server configuration will be
        tested.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            4.8
        """

        url = "/file/s3_test".format()

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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def get_config(
        self,
    ) -> Config:
        """Get configuration

        Retrieve the current server configuration

        Permissions:
            Must have `manage_system` permission.
        """

        url = "/config".format()

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
            response_200 = Config.parse_obj(response.json())

            return response_200
        return response

    async def update_config(
        self,
        *,
        json_body: Config,
    ) -> Config:
        """Update configuration

        Submit a new configuration for the server to use. As of server version
        4.8, the `PluginSettings.EnableUploads` setting cannot be modified by
        this endpoint.

        Permissions:
            Must have `manage_system` permission.
        """

        url = "/config".format()

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.put(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = Config.parse_obj(response.json())

            return response_200
        return response

    async def reload_config(
        self,
    ) -> StatusOK:
        """Reload configuration

        Reload the configuration file to pick up on any changes made to it.

        Permissions:
            Must have `manage_system` permission.
        """

        url = "/config/reload".format()

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

    async def get_client_config(
        self,
        *,
        format: str,
    ) -> None:
        """Get client configuration

        Get a subset of the server configuration needed by the client.

        Permissions:
            No permission required.
        """

        url = "/config/client".format()
        params: Dict[str, Any] = {
            "format": format,
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

        return response

    async def get_environment_config(
        self,
    ) -> EnvironmentConfig:
        """Get configuration made through environment variables

        Retrieve a json object mirroring the server configuration where fields
        are set to true
        if the corresponding config setting is set through an environment
        variable. Settings
        that haven't been set through environment variables will be missing from
        the object.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            4.10
        """

        url = "/config/environment".format()

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
            response_200 = EnvironmentConfig.parse_obj(response.json())

            return response_200
        return response

    async def patch_config(
        self,
        *,
        json_body: Config,
    ) -> Config:
        """Patch configuration

        Submit configuration to patch. As of server version 4.8, the
        `PluginSettings.EnableUploads` setting cannot be modified by this
        endpoint.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.20
        """

        url = "/config/patch".format()

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.put(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = Config.parse_obj(response.json())

            return response_200
        return response

    async def migrate_config(
        self,
        *,
        json_body: MigrateConfigJsonBody,
    ) -> StatusOK:
        """Migrate configuration

        Migrate a file-based configuration to (or from) a database-based
        configuration.
        Point the Mattermost server at the target configuration to start using
        it.

        Permissions:
            Must have `manage_system` permission
        Minimum Server Version:
            5.26
        """

        url = "/config/migrate".format()

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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def upload_license_file(
        self,
        *,
        multipart_data: UploadLicenseFileMultipartData,
    ) -> StatusOK:
        """Upload license file

        Upload a license to enable enterprise features.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            4.0
        """

        url = "/license".format()

        multipart_body_data = UploadLicenseFileMultipartData.parse_obj(multipart_data)

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

    async def remove_license_file(
        self,
    ) -> None:
        """Remove license file

        Remove the license file from the server. This will disable all
        enterprise features.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            4.0
        """

        url = "/license".format()

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.delete(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        return response

    async def get_client_license(
        self,
        *,
        format: str,
    ) -> None:
        """Get client license

        Get a subset of the server license needed by the client.

        Permissions:
            No permission required but having the `manage_system` permission
        returns more information.
        """

        url = "/license/client".format()
        params: Dict[str, Any] = {
            "format": format,
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

        return response

    async def request_license_renewal_link(
        self,
    ) -> LicenseRenewalLink:
        """Request the license renewal link

        Request the renewal link that would be used to start the license renewal
        process

        Permissions:
            Must have `sysconsole_write_about` permission.
        Minimum Server Version:
            5.32
        """

        url = "/license/renewal".format()

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
            response_200 = LicenseRenewalLink.parse_obj(response.json())

            return response_200
        return response

    async def request_trial_license(
        self,
        *,
        json_body: RequestTrialLicenseJsonBody,
    ) -> None:
        """Request and install a trial license for your server

        Request and install a trial license for your server

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.25
        """

        url = "/trial-license".format()

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

        return response

    async def get_trial_license_prev(
        self,
    ) -> None:
        """Get last trial license used

        Get the last trial license used on the sevrer

        Permissions:
            Must have `manage_systems` permissions.
        Minimum Server Version:
            5.36
        """

        url = "/trial-license/prev".format()

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        return response

    async def get_audits(
        self,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> List[Audit]:
        """Get audits

        Get a page of audits for all users on the system, selected with `page`
        and `per_page` query parameters.

        Permissions:
            Must have `manage_system` permission.
        """

        url = "/audits".format()
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
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
                response_200_item = Audit.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    async def invalidate_caches(
        self,
    ) -> StatusOK:
        """Invalidate all the caches

        Purge all the in-memory caches for the Mattermost server. This can have
        a temporary negative effect on performance while the caches are re-
        populated.

        Permissions:
            Must have `manage_system` permission.
        """

        url = "/caches/invalidate".format()

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

    async def get_logs(
        self,
        *,
        page: Optional[int] = 0,
        logs_per_page: Optional[str] = "10000",
    ) -> List[str]:
        """Get logs

        Get a page of server logs, selected with `page` and `logs_per_page`
        query parameters.

        Permissions:
            Must have `manage_system` permission.
        """

        url = "/logs".format()
        params: Dict[str, Any] = {
            "page": page,
            "logs_per_page": logs_per_page,
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
            response_200 = cast(List[str], response.json())

            return response_200
        return response

    async def post_log(
        self,
        *,
        json_body: PostLogJsonBody,
    ) -> PostLogResponse_200:
        """Add log message

        Add log messages to the server logs.
        Logged in users can log ERROR or DEBUG messages when
        `ServiceSettings.EnableDeveloper` is `true` or just DEBUG messages when
        `false`.
        Non-logged in users can log ERROR or DEBUG messages when
        `ServiceSettings.EnableDeveloper` is `true` and cannot log when `false`.

        Permissions:
            Users with `manage_system` permission can log ERROR or DEBUG
        messages.
        """

        url = "/logs".format()

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
            response_200 = PostLogResponse_200.parse_obj(response.json())

            return response_200
        return response

    async def get_analytics_old(
        self,
        *,
        name: Optional[str] = "standard",
        team_id: Optional[str] = None,
    ) -> None:
        """Get analytics

        Get some analytics data about the system. This endpoint uses the old
        format, the `/analytics` route is reserved for the new format when it
        gets implemented.

        The returned JSON changes based on the `name` query parameter but is
        always key/value pairs.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            4.0
        """

        url = "/analytics/old".format()
        params: Dict[str, Any] = {
            "name": name,
            "team_id": team_id,
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

        return response

    async def get_server_busy_expires(
        self,
    ) -> Server_Busy:
        """Get server busy expiry time.

        Gets the timestamp corresponding to when the server busy flag will be
        automatically cleared.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.20
        """

        url = "/server_busy".format()

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
            response_200 = Server_Busy.parse_obj(response.json())

            return response_200
        return response

    async def set_server_busy(
        self,
        *,
        seconds: Optional[str] = "3600",
    ) -> StatusOK:
        """Set the server busy (high load) flag

        Marks the server as currently having high load which disables non-
        critical services such as search, statuses and typing notifications.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.20
        """

        url = "/server_busy".format()
        params: Dict[str, Any] = {
            "seconds": seconds,
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

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def clear_server_busy(
        self,
    ) -> StatusOK:
        """Clears the server busy (high load) flag

        Marks the server as not having high load which re-enables non-critical
        services such as search, statuses and typing notifications.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.20
        """

        url = "/server_busy".format()

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

    async def get_redirect_location(
        self,
        *,
        url: str,
    ) -> None:
        """Get redirect location



        Permissions:
            Must be logged in.
        Minimum Server Version:
            3.10
        """

        url = "/redirect_location".format()
        params: Dict[str, Any] = {
            "url": url,
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

        return response

    async def get_image_by_url(
        self,
    ) -> None:
        """Get an image by url

        Fetches an image via Mattermost image proxy.

        Permissions:
            Must be logged in.
        Minimum Server Version:
            3.10
        """

        url = "/image".format()

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        return response

    async def upgrade_to_enterprise(
        self,
    ) -> PushNotification:
        """Executes an inplace upgrade from Team Edition to Enterprise Edition

        It downloads the Mattermost Enterprise Edition of your current version
        and replace your current version with it. After the upgrade you need to
        restart the Mattermost server.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.27
        """

        url = "/upgrade_to_enterprise".format()

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 202:
            response_202 = PushNotification.parse_obj(response.json())

            return response_202
        return response

    async def upgrade_to_enterprise_status(
        self,
    ) -> UpgradeToEnterpriseStatusResponse_200:
        """Get the current status for the inplace upgrade from Team Edition to
        Enterprise Edition

        It returns the percentage of completion of the current upgrade or the
        error if there is any.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.27
        """

        url = "/upgrade_to_enterprise/status".format()

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
            response_200 = UpgradeToEnterpriseStatusResponse_200.parse_obj(
                response.json()
            )

            return response_200
        return response

    async def restart_server(
        self,
    ) -> StatusOK:
        """Restart the system after an upgrade from Team Edition to Enterprise
        Edition

        It restarts the current running mattermost instance to execute the new
        Enterprise binary.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.27
        """

        url = "/restart".format()

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

    async def get_warn_metrics_status(
        self,
    ) -> StatusOK:
        """Get the warn metrics status (enabled or disabled)

        Get the status of a set of metrics (enabled or disabled) from the
        Systems table.

        The returned JSON contains the metrics that we need to warn the admin on
        with regard
        to their status (we return the ones whose status is \"true\", which
        means that they are
        in a \"warnable\" state - e.g. a threshold has been crossed or some
        other condition has
        been fulfilled).

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.26
        """

        url = "/warn_metrics/status".format()

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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def send_warn_metric_ack(
        self,
        warn_metric_id: str,
        *,
        json_body: SendWarnMetricAckJsonBody,
    ) -> StatusOK:
        """Acknowledge a warning of a metric status

        Acknowledge a warning for the warn_metric_id metric crossing a threshold
        (or some
        similar condition being fulfilled) - attempts to send an ack email to
        acknowledge@mattermost.com and sets the \"ack\" status for all the warn
        metrics in the system.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.26
        """

        url = "/warn_metrics/ack/{warn_metric_id}".format(
            warn_metric_id=warn_metric_id,
        )

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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def send_trial_license_warn_metric_ack(
        self,
        warn_metric_id: str,
    ) -> StatusOK:
        """Request trial license and acknowledge a warning of a metric status

        Request a trial license and acknowledge a warning for the warn_metric_id
        metric crossing a threshold (or some
        similar condition being fulfilled) - sets the \"ack\" status for all the
        warn metrics in the system.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.28
        """

        url = "/warn_metrics/trial-license-ack/{warn_metric_id}".format(
            warn_metric_id=warn_metric_id,
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

    async def check_integrity(
        self,
    ) -> List[IntegrityCheckResult]:
        """Perform a database integrity check

        Performs a database integrity check.

        Minimum Server Version:
            5.28.0
        Local Mode Only:
            This endpoint is only available through [local
        mode](https://docs.mattermost.com/administration/mmctl-cli-
        tool.html#local-mode).

        Warning:
            This check may temporarily harm system performance.
        """

        url = "/integrity".format()

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
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = IntegrityCheckResult.parse_obj(
                    response_200_item_data
                )

                response_200.append(response_200_item)

            return response_200
        return response

    async def generate_support_packet(
        self,
    ) -> None:
        """Download a zip file which contains helpful and useful information for
        troubleshooting your mattermost instance.

        Download a zip file which contains helpful and useful information for
        troubleshooting your mattermost instance.
        ##### License
        Requires either a E10 or E20 license.

        Permissions:
            Must have any of the system console read permissions.
        Minimum Server Version:
            5.32
        """

        url = "/system/support_packet".format()

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        return response

    async def update_marketplace_visited_by_admin(
        self,
        *,
        json_body: System,
    ) -> StatusOK:
        """Stores that the Plugin Marketplace has been visited by at least an
        admin.

        Stores the system-level status that specifies that at least an admin has
        visited the in-product Plugin Marketplace.

        Permissions:
            Must have `manage_system` permissions.
        Minimum Server Version:
            5.33
        """

        url = "/plugins/marketplace/first_admin_visit".format()

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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response
