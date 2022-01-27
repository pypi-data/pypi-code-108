from typing import Callable, Dict, List, Optional, Union

from requests.models import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.utils._client_config import ClientConfig
from cognite.well_model.wsfe.models import ProcessIdItems, ProcessState, ProcessStateItems, SubmitJob, SubmitRequest
from cognite.well_model.wsfe.process_state_list import ProcessStateList


class WellLogExtractorClient:
    """Entrypoint to everything about the wsfe.

    Args:
        api_key (Optional[str], optional): API key
        project (Optional[str], optional): Project
        cluster (str, optional): api, greenfield, bluefield, azure-dev, etc. Defaults to "api".
        client_name (str, optional): A user-defined name for the client.
            Used to identify number of unique applications/scripts running
            on top of CDF.
        base_url (Optional[str], optional): Defaults to "https://wsfe.cognitedata-production.cognite.ai".
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

    Examples:
        Create a client:
            >>> from cognite.well_model.wsfe import WellLogExtractorClient
            >>> wlec = WellLogExtractorClient()
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        project: Optional[str] = None,
        cluster: str = "api",
        # Unused, but we'll leave it be for consistency with other Cognite clients
        client_name: str = None,
        base_url: Optional[str] = "https://wsfe.cognitedata-production.cognite.ai",
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
            cluster=cluster,
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

        self.cluster = self._config.cluster
        self.project = self._config.project

        self._api_client = APIClient(self._config, cognite_client=self)

    def _path(self, component: str) -> str:
        component = component.lstrip("/")
        return f"/v1/{self.cluster}/{self.project}/{component}"

    def submit(self, items: List[SubmitJob], overwrite_sequences: bool = False) -> ProcessStateList:
        """Submit a set of files to extraction

        Args:
            items (List[SubmitJob]): items to extract
            overwrite_sequences (bool, optional): Set to true to overwrite sequences if they already exist.

        Returns:
            ProcessStateList: Status object

        Examples:
            Submit a file for extraction and wait
                >>> from cognite.well_model.wsfe import WellLogExtractorClient
                >>> from cognite.well_model.wsfe.models import (
                ...    FileType,
                ...    JobDestination,
                ...    JobSource,
                ...    SubmitJob,
                ... )
                >>> wlec = WellLogExtractorClient()
                >>> job = SubmitJob(
                ...     source=JobSource(
                ...         file_external_id="WEL_Laverda_East_1_S1R2_CMR_Main_Pass_025PUC.dlis",
                ...         file_type=FileType.dlis,
                ...     ),
                ...     destination=JobDestination(
                ...         data_set_external_id="volve",
                ...     ),
                ...     contains_trajectory=False,
                ... )
                >>> status = wlec.submit([job]) # doctest: +SKIP
                >>> status.wait() # doctest: +SKIP

            The valid file types are
                >>> from cognite.well_model.wsfe.models import FileType
                >>> file_types = [
                ...     FileType.dlis,
                ...     FileType.las,
                ...     FileType.asc
                ... ]
        """
        request = SubmitRequest(
            write_to_wdl=False,
            create_assets=False,
            contextualize_with_assets=False,
            items=items,
            overwrite_sequences=overwrite_sequences,
        )

        response: Response = self._api_client.post(self._path("submit"), json=request.json())
        content: ProcessStateItems = ProcessStateItems.parse_raw(response.text)
        items = content.items
        return ProcessStateList(self, items)

    def status(self, process_ids: List[int]) -> ProcessStateList:
        """Retrieve the status of a set of items previously submitted for extraction"""
        request = ProcessIdItems(items=process_ids)

        response: Response = self._api_client.post(self._path("status"), json=request.json())
        content: ProcessStateItems = ProcessStateItems.parse_raw(response.text)
        items: List[ProcessState] = content.items
        return ProcessStateList(self, items)

    def status_report(self, statuses: List[ProcessState]) -> Dict[str, int]:
        """Partition the set of statuses based on whether they are 'ready', 'processing', 'done' or 'error'"""
        status_types = set(s["status"] for s in statuses)
        return {state: sum(1 for s in statuses if s["status"] == state) for state in status_types}
