from typing import Any, Dict, List

import requests

from fastel.logistics.models import TcatLogsiticsData, TcatPickingData


class TcatClient:
    default_headers = {
        "Content-Type": "application/json",
    }

    @property
    def url(self) -> str:
        if self.stage in ["stg", "STG"]:
            return "http://apitestsuda.southeastasia.cloudapp.azure.com:8081/api/Egs"
        return "https://api.suda.com.tw/api/Egs"

    def __init__(self, stage: str, client_id: str, client_token: str):
        self.stage = stage
        self._client_id = client_id
        self._client_token = client_token

    def _get(self, path: str) -> Any:
        full_url = f"{self.url}{path}"
        resp = requests.get(url=full_url, headers=self.default_headers)
        resp.raise_for_status()
        return resp

    def _post(self, path: str, data: Dict[str, Any]) -> Any:
        full_url = f"{self.url}{path}"
        resp = requests.post(url=full_url, json=data, headers=self.default_headers)
        resp.raise_for_status()
        return resp

    def query_postal_number(self, addresses: List[str]) -> Dict[str, Any]:
        address_array = [{"Search": address} for address in addresses]
        json_data = {
            "CustomerId": self._client_id,
            "CustomerToken": self._client_token,
            "Addresses": address_array,
        }
        resp = self._post("/ParsingAddress", json_data)
        return resp.json()  # type: ignore

    def create_logistics(self, data: TcatLogsiticsData) -> Dict[str, Any]:
        data_dict = data.dict(exclude_none=True)

        json_data = {
            "CustomerId": self._client_id,
            "CustomerToken": self._client_token,
            **data_dict,
        }
        resp = self._post("/PrintOBT", json_data)
        return resp.json()  # type: ignore

    def create_picking_list(self, data: TcatPickingData) -> Dict[str, Any]:
        data_dict = data.dict(exclude_none=True)

        json_data = {
            "CustomerId": self._client_id,
            "CustomerToken": self._client_token,
            **data_dict,
        }
        resp = self._post("/PrintOBTByPickingList", json_data)
        return resp.json()  # type: ignore

    def download_logistics_pdf(self, FileNo: str) -> Dict[str, Any]:
        json_data = {
            "CustomerId": self._client_id,
            "CustomerToken": self._client_token,
            "FileNo": FileNo,
        }
        resp = self._post("/DownloadOBT", json_data)
        return {"file": resp.content}
