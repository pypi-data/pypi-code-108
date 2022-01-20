from contextlib import contextmanager
from typing import Union, List, Iterable

from msgraphy.client.graph_client import GraphClient, GraphResponse
from msgraphy.data import ApiIterable
from msgraphy.data.file import DriveItem
from msgraphy.data.workbook import WorkbookSessionInfo, WorkbookRange, Table, WorkbookTableRow, WorkbookTableColumn


class WorkbookGraphApi:

    def __init__(self, api: "....GraphApi"):
        self._api = api

    def list_tables(self, drive_item: DriveItem) -> Iterable[Table]:
        resource = f"{drive_item.get_api_reference()}/workbook/tables"
        return self._api.client.make_request(url=resource, response_type=ApiIterable(self._api.client, Table))

    def create_session(self, drive_item: DriveItem) -> WorkbookSessionInfo:
        resource = f"{drive_item.get_api_reference()}/workbook/createSession"
        response = self._api.client.make_request(url=resource, method="post")
        return WorkbookSessionInfo(response.value, workbook_reference=drive_item)

    def close_session(self, session: WorkbookSessionInfo):
        resource = f"{session.workbook_reference.get_api_reference()}/workbook/closeSession"
        self._api.client.make_request(url=resource, method="post", headers=session.headers())

    @contextmanager
    def session_context(self, drive_item: DriveItem):
        session = self.create_session(drive_item)
        try:
            yield session
        finally:
            self.close_session(session)

    def get_table_api(self, table_name: str, workbook: Union[DriveItem, WorkbookSessionInfo]):
        if isinstance(workbook, WorkbookSessionInfo):
            return TableGraphApi(self._api, workbook.workbook_reference, table_name, workbook)
        else:
            return TableGraphApi(self._api, workbook, table_name)


class TableGraphApi:

    def __init__(self, api: "....GraphApi", workbook: DriveItem, table_name: str, session: WorkbookSessionInfo = None):
        self._api = api
        self._workbook = workbook
        self._table_name = table_name
        self._session = session
        self._root_resource = f"{workbook.get_api_reference()}/workbook/tables/{table_name}"

        table_api = self

        class _Client(GraphClient):
            def make_request(self, url="", headers=None, **kwargs):
                """ We use an internal method to make requests and ensure we always have session info if set"""
                if table_api._session:
                    headers = {**headers, **table_api._session.headers()} if headers else {
                        **table_api._session.headers()}
                if url.startswith("/"):
                    url = f"{table_api._root_resource}{url}"
                else:
                    url = f"{table_api._root_resource}/{url}"
                return table_api._api.client.make_request(url, headers=headers, **kwargs)

        self.client = _Client()

    def get_table(self, select: str = None) -> GraphResponse[Table]:
        params = {}
        if select:
            params['$select'] = select
        return self.client.make_request(params=params, response_type=Table)

    def get_rows(self, index: int = None, top: int = None, skip: int = None) -> GraphResponse[Iterable[WorkbookTableRow]]:
        resource = "/rows"
        params = None
        if index is not None:
            resource += f"/itemAt(index={index})"
        else:
            params = {}
            if top is not None:
                params['$top'] = top
            if skip is not None:
                params['$skip'] = skip

        return self.client.make_request(resource, params=params,
                                        response_type=ApiIterable(self.client, WorkbookTableRow))

    def get_columns(self, index: int = None, top: int = None, skip: int = None) -> GraphResponse[Iterable[WorkbookTableColumn]]:
        resource = f"/columns"
        params = None
        if index is not None:
            resource += f"/itemAt(index={index})"
        else:
            params = {}
            if top is not None:
                params['$top'] = top
            if skip is not None:
                params['$skip'] = skip

        return self.client.make_request(resource, params=params,
                                        response_type=ApiIterable(self.client, WorkbookTableColumn))

    def get_range(self, select=None) -> GraphResponse[WorkbookRange]:
        resource = f"/range"
        params = {}
        if select:
            params['$select'] = select
        return self.client.make_request(url=resource, params=params, response_type=WorkbookRange)

    def get_data_body_range(self, select=None) -> GraphResponse[WorkbookRange]:
        resource = f"/dataBodyRange"
        params = {}
        if select:
            params['$select'] = select
        return self.client.make_request(url=resource, params=params, response_type=WorkbookRange)

    def get_header_row_range(self, select=None) -> GraphResponse[WorkbookRange]:
        resource = f"/headerRowRange"
        params = {}
        if select:
            params['$select'] = select
        return self.client.make_request(url=resource, params=params, response_type=WorkbookRange)

    def add_rows(self, values: List) -> GraphResponse:
        resource = f"/rows/add"
        return self.client.make_request(url=resource, json=dict(values=values), method="post")

    def update_row(self, index: int, values: List) -> GraphResponse:
        resource = f"/rows/itemAt(index={index})"
        return self.client.make_request(url=resource, json=dict(index=index, values=values), method="patch")

    def delete_row(self, index: int) -> GraphResponse:
        resource = f"/rows/itemAt(index={index})"
        return self.client.make_request(url=resource, method="delete")

    def delete_range(self) -> GraphResponse:
        resource = f"/range/delete"
        return self.client.make_request(url=resource, method="post")

    def delete_data_body_range(self) -> GraphResponse:
        resource = f"/dataBodyRange/delete"
        return self.client.make_request(url=resource, method="post")

    def get_filter_criteria(self, index: int) -> GraphResponse:
        resource = f"/columns/itemAt(index={index})/filter"
        return self.client.make_request(url=resource, method="get")
