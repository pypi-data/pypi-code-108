from typing import Callable, Dict, List, Optional, Union

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.casings import CasingsAPI
from cognite.well_model.client.api.depth_measurements import DepthMeasurementsAPI
from cognite.well_model.client.api.mnemonics import MnemonicsAPI
from cognite.well_model.client.api.nds_events import NdsEventsAPI
from cognite.well_model.client.api.npt_events import NptEventsAPI
from cognite.well_model.client.api.sources import SourcesAPI
from cognite.well_model.client.api.summaries import SummariesAPI
from cognite.well_model.client.api.time_measurements import TimeMeasurementsAPI
from cognite.well_model.client.api.trajectories import TrajectoriesAPI
from cognite.well_model.client.api.well_tops import WellTopsAPI
from cognite.well_model.client.api.wellbores import WellboresAPI
from cognite.well_model.client.api.wells import WellsAPI
from cognite.well_model.client.utils._client_config import ClientConfig


# from cognite.well_model.client.api.sources import SourcesAPI
class CogniteWellsClient:
    """All services are made available through this object. See examples below.

    Args:
        api_key (str): API key
        project (str): Project. Defaults to project of given API key.
        client_name (str): A user-defined name for the client. Used to identify number of unique applications/scripts
            running on top of CDF.
        base_url (str): Base url to send requests to.
        max_workers (int): Max number of workers to spawn when parallelizing data fetching. Defaults to 10.
        headers (Dict): Additional headers to add to all requests.
        timeout (int): Timeout on requests sent to the api. Defaults to 60 seconds.
        token (Union[str, Callable]): token (Union[str, Callable[[], str]]): A jwt or method which takes no arguments
            and returns a jwt to use for authentication.
        token_url (str): Optional url to use for token generation
        token_client_id (str): Optional client id to use for token generation.
        token_client_secret (str): Optional client secret to use for token generation.
        token_scopes (list): Optional list of scopes to use for token generation.
        token_custom_args (Dict): Optional additional arguments to use for token generation.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        project: Optional[str] = None,
        client_name: Optional[str] = None,
        base_url: Optional[str] = None,
        max_workers: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        token: Optional[Union[str, Callable[[], str], None]] = None,
        token_url: Optional[str] = None,
        token_client_id: Optional[str] = None,
        token_client_secret: Optional[str] = None,
        token_scopes: Optional[List[str]] = None,
        token_custom_args: Dict[str, str] = None,
    ):
        self._config = ClientConfig(
            api_key=api_key,
            project=project,
            client_name=client_name,
            base_url=base_url,
            max_workers=max_workers,
            headers=headers,
            timeout=timeout,
            token=token,
            token_url=token_url,
            token_client_id=token_client_id,
            token_client_secret=token_client_secret,
            token_scopes=token_scopes,
            token_custom_args=token_custom_args,
        )

        self._api_client = APIClient(self._config, cognite_client=self)
        self.wellbores = WellboresAPI(client=self._api_client)
        self.npt = NptEventsAPI(client=self._api_client)
        self.nds = NdsEventsAPI(client=self._api_client)
        self.wells = WellsAPI(client=self._api_client)
        self.trajectories = TrajectoriesAPI(client=self._api_client)
        self.depth_measurements = DepthMeasurementsAPI(client=self._api_client)
        self.time_measurements = TimeMeasurementsAPI(client=self._api_client)
        self.sources = SourcesAPI(self._api_client)
        self.casings = CasingsAPI(self._api_client)
        self.mnemonics = MnemonicsAPI(self._api_client)
        self.well_tops = WellTopsAPI(self._api_client)
        self.summaries = SummariesAPI(self._api_client)

    @property
    def config(self) -> ClientConfig:
        """Configuration for the current client."""
        return self._config
