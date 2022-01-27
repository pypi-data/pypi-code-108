from typing import Any, Optional, Union

from botocore.client import BaseClient
from botocore.config import Config


class Session:
    def client(
        self,
        service_name: str,
        region_name: Optional[str] = None,
        api_version: Optional[str] = None,
        use_ssl: Optional[bool] = None,
        verify: Optional[Union[str, bool]] = None,
        endpoint_url: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        config: Optional[Config] = None,
    ) -> BaseClient:
        pass

    def resource(
        self,
        service_name: str,
        region_name: Optional[str] = None,
        api_version: Optional[str] = None,
        use_ssl: Optional[bool] = None,
        verify: Optional[Union[str, bool]] = None,
        endpoint_url: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        config: Optional[Config] = None,
    ) -> Any:
        pass
