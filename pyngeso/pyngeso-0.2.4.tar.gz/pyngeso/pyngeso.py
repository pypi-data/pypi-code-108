import logging
from typing import Optional, List, Literal
from datetime import datetime
import json
import re

import requests

from .configure_logging import setup_logger
from .resources import api_resource_ids, file_resource_ids
from .exceptions import UnsuccessfulRequest

logger = setup_logger(logging.getLogger("PyNgEso"))


class NgEso:
    """
    A class for fetching data from the National Grid ESO data portal.

    Args:
        resource_id (str): id for the resource when using the ESO API functionality
        resource (str): name of the resource when using the ESO API functionality
    Returns:

    """
    def __init__(
            self,
            resource: str,
            backend: Literal['api', 'file'] = "api"
    ):
        self.resource = resource
        self.backend = backend

        self.resource_id, self.dataset_id, self.filename = self.set_resource_info()

    def set_resource_info(self) -> (str, str, str):
        dataset_id = None
        filename = None
        if self.backend == "api":
            resource_id = api_resource_ids.get(self.resource).get("id")
        else:
            dataset_id = file_resource_ids.get(self.resource).get("dataset_id")
            resource_id = file_resource_ids.get(self.resource).get("resource_id")
            filename = file_resource_ids.get(self.resource).get("filename")
        return resource_id, dataset_id, filename

    def query(
        self,
        fields: Optional[List[str]] = None,
        date_col: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        filters: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> bytes:

        url = f"https://data.nationalgrideso.com/api/3/action/datastore_search_sql"
        sql = self.construct_sql(fields, date_col, start_date, end_date, filters, limit)
        params = {"sql": sql}

        logger.debug(f"Querying {self.resource}: {sql}")
        r = requests.get(url, params=params)
        self._check_for_errors(r)
        self._missing_data(r)

        return r.content

    def construct_sql(
        self,
        fields: Optional[List[str]] = None,
        date_col: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        filters: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> str:
        fields_sql = "*"
        date_filter_sql = ""
        filter_sql = ""
        limits_sql = ""

        if fields:
            # double quote all fields
            fields_sql = ", ".join([f'"{i}"' for i in fields])

        date_filtering = date_col is not None
        if date_filtering:
            date_filter_sql = self.construct_date_range(date_col, start_date, end_date)

        if filters:
            filter_sql = self.construct_filter_sql(filters, date_filtering)

        if limit:
            limits_sql = f"limit {limit}"

        sql = " ".join([
            "select",
            fields_sql,
            "from",
            f'"{self.resource_id}"',
            date_filter_sql,
            filter_sql,
            limits_sql]
        )

        return sql

    def construct_date_range(
        self,
        date_col: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> str:
        if start_date:
            self.validate_date_fmt(start_date)
        if end_date:
            self.validate_date_fmt(end_date)

        dates_provided = (start_date is not None, end_date is not None)
        # validation of dates
        if not any(dates_provided):
            raise ValueError("At least one of {start_date,end_date} should be provided")
        if all(dates_provided):
            self.validate_date_range(start_date, end_date)

        date_range_map = {
            (True, False): f"where \"{date_col}\" >= '{start_date}'::timestamp",
            (False, True): f"where \"{date_col}\" < '{end_date}'::timestamp",
            (
                True,
                True,
            ): f"where \"{date_col}\" BETWEEN '{start_date}'::timestamp "
               f"and '{end_date}'::timestamp",
        }
        date_filter_sql = date_range_map.get(dates_provided)

        return date_filter_sql

    @staticmethod
    def construct_filter_sql(filters: List[str], date_filtering: bool) -> str:
        cond_join = " and "
        filters_sql = cond_join.join(filters)
        # if filtering by date "WHERE' clause is already added
        if date_filtering:
            return "and " + filters_sql
        return "where " + filters_sql

    @staticmethod
    def validate_date_fmt(date_: str) -> None:
        reg = r"^20\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
        if re.search(reg, date_) is None:
            raise ValueError(f"date {date_} does not match format '%Y-%m-%d'")

    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> None:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        assert (
            end_date >= start_date
        ), "end_date should be the same of greater than start_date"

    def _check_for_errors(self, r: requests.Response) -> None:
        """Inspect the request response and the metadata in xml"""
        # http response errors
        self._check_request_errors(r)

        # inspect response body
        rb: dict = json.loads(r.content)
        if not rb.get("success"):
            logger.error(f"Request failed: {rb.get('error')}")

    @staticmethod
    def _check_request_errors(r: requests.Response) -> None:
        status_code = r.status_code
        if status_code != 200 or r.content is None:
            raise UnsuccessfulRequest(f"status_code={status_code}:{r.content}")

    @staticmethod
    def _missing_data(r: requests.Response) -> None:
        """
        The ESO API does not report for no data found. The result section of the
        response cam be inspected and log if none were found
        """
        rb = json.loads(r.content)
        records = rb.get("result").get("records")
        query = rb.get("query")
        if not records:
            logger.warning(f"{query}: No data found")

    def download_file(self) -> bytes:
        url = (
            f"https://data.nationalgrideso.com/backend/dataset/{self.dataset_id}/"
            f"resource/{self.resource_id}/download/{self.filename}"
        )
        r = requests.get(url)
        self._check_request_errors(r)

        return r.content
