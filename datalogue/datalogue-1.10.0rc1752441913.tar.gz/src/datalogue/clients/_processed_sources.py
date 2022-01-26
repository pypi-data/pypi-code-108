from typing import Optional, Union, List, Dict, Tuple, Iterator

from datalogue.clients._http import _HttpClient, HttpMethod
from datalogue.errors import DtlError
from datalogue.dtl_utils import _parse_list, _parse_string_list
from uuid import UUID


class ProcessedSourceWithStatus:
    def __init__(self, source_name: str, job_id: UUID, status: str):
        self.source_name = source_name
        self.job_id = job_id
        self.status = status

    def __repr__(self):
        return f"(source_name: {self.source_name}, " f"job_id: {self.job_id}, " f"status: {self.status})"


def _parse_processed_source_with_status(json: dict,) -> Union[ProcessedSourceWithStatus, ProcessedSourceWithStatus]:
    source_name = json.get("sourceName")
    if source_name is None:
        return DtlError("'sourceName' for a processed source should be defined")

    job_id = json.get("jobId")
    if job_id is None:
        return DtlError("'jobId' for a processed source should be defined")

    status = json.get("status")
    if status is None:
        return DtlError("'status' for a processed source should be defined")

    return ProcessedSourceWithStatus(source_name, job_id, status)


class _ProcessedSourcesClient:
    """
    Client to get processed sources list for different ids
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/scout"

    """
    Return the files already processed by the specified job
    """

    def get_by_job_id(self, job_id: Union[str, UUID]) -> List[str]:
        url = f"{self.service_uri}/jobs/{str(job_id)}/sources/lock"
        res = self.http_client.execute_authed_request(url, HttpMethod.GET)
        if isinstance(res, DtlError):
            return res
        return _parse_string_list(res.json())

    """
    Return the files already processed by the specified connection/credential
    """

    def get_by_credential_id(self, credential_id: Union[str, UUID]):
        url = f"{self.service_uri}/credentials/{str(credential_id)}/sources/lock"
        res = self.http_client.execute_authed_request(url, HttpMethod.GET)
        if isinstance(res, DtlError):
            return res
        return _parse_list(_parse_processed_source_with_status)(res.json())

    """
    Return the files already processed by the specified pipeline
    """

    def get_by_stream_id(self, stream_id: Union[str, UUID]):
        url = f"{self.service_uri}/streams/{str(stream_id)}/sources/lock"
        res = self.http_client.execute_authed_request(url, HttpMethod.GET)
        if isinstance(res, DtlError):
            return res
        return _parse_list(_parse_processed_source_with_status)(res.json())
