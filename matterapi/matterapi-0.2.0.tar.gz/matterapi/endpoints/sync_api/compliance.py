from typing import Any, Dict, List, Optional

from ...models import Compliance
from ..base import ApiBaseClass


class ComplianceApi(ApiBaseClass):
    """Endpoints for creating, getting and downloading compliance reports."""

    def get_compliance_reports(
        self,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> List[Compliance]:
        """Get reports

        Get a list of compliance reports previously created by page, selected
        with `page` and `per_page` query parameters.

        Permissions:
            Must have `manage_system` permission.
        """

        url = "/compliance/reports".format()
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
        }
        params = {k: v for k, v in params.items() if v is not None}

        request_kwargs = {
            "url": url,
            "params": params,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = Compliance.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def create_compliance_report(
        self,
    ) -> Compliance:
        """Create report

        Create and save a compliance report.

        Permissions:
            Must have `manage_system` permission.
        """

        url = "/compliance/reports".format()

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = Compliance.parse_obj(response.json())

            return response_201
        return response

    def get_compliance_report(
        self,
        report_id: str,
    ) -> Compliance:
        """Get a report

        Get a compliance reports previously created.

        Permissions:
            Must have `manage_system` permission.
        """

        url = "/compliance/reports/{report_id}".format(
            report_id=report_id,
        )

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = Compliance.parse_obj(response.json())

            return response_200
        return response

    def download_compliance_report(
        self,
        report_id: str,
    ) -> None:
        """Download a report

        Download the full contents of a report as a file.

        Permissions:
            Must have `manage_system` permission.
        """

        url = "/compliance/reports/{report_id}/download".format(
            report_id=report_id,
        )

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        return response
