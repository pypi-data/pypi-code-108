"""
API object to talk to a model
"""
import typing as t

from taktile_types.schemas.deployment.endpoint import InfoEndpointResponseModel

from taktile_client.http_client import API


class Model(API):
    """Model api object"""

    def __init__(
        self,
        url: str,
        api_key: t.Optional[str],
        headers: t.Optional[t.Dict[str, str]] = None,
    ):
        super().__init__(api_base=url, api_key=api_key, headers=headers)

    def get_info(self) -> InfoEndpointResponseModel:
        """Retrieve model info

        Returns
        -------
        InfoEndpointResponseModel
            info endpoint response model
        """
        return t.cast(
            InfoEndpointResponseModel,
            self.call(
                verb="get", path="/info", model=InfoEndpointResponseModel
            ),
        )
