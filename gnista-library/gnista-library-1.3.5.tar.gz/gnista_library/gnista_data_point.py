import json
import uuid
from typing import Any, List, Type, TypeVar, Union

import pandas as pd
from pandas import DataFrame
from structlog import get_logger

from data_point_client import AuthenticatedClient
from data_point_client.api.data_point import (
    data_point_append_time_series_data,
    data_point_append_time_series_data_2,
    data_point_create_data_point,
    data_point_create_data_point_2,
    data_point_get_data,
    data_point_get_data_2,
    data_point_get_data_point,
    data_point_get_data_point_2,
    data_point_update_constant_data,
    data_point_update_constant_data_2,
    data_point_update_time_series_data,
    data_point_update_time_series_data_2,
)
from data_point_client.models import GetConstantResponse, GetSeriesResponse
from data_point_client.models.append_time_series_request import AppendTimeSeriesRequest
from data_point_client.models.data_point_request import DataPointRequest
from data_point_client.models.en_data_point_existence_dto import EnDataPointExistenceDTO
from data_point_client.models.get_data_request import GetDataRequest
from data_point_client.models.problem_details import ProblemDetails
from data_point_client.models.sub_series_request import SubSeriesRequest
from data_point_client.models.sub_series_request_values import SubSeriesRequestValues
from data_point_client.models.time_series_response_curve import TimeSeriesResponseCurve
from data_point_client.models.update_constant_data_request import UpdateConstantDataRequest
from data_point_client.models.update_time_series_request import UpdateTimeSeriesRequest
from data_point_client.types import Response, Unset

from .gnista_connetion import GnistaConnection

log = get_logger()

# pylint: disable=C0103
T = TypeVar("T", bound="GnistaDataPoint")


class GnistaDataPoint:
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    DATE_NAME = "Date"
    VALUE_NAME = "Value"

    @classmethod
    def create_new(cls: Type[T], connection: GnistaConnection, name: str, tags: List[str]) -> Union[T, None]:
        token = connection.get_access_token()
        client = AuthenticatedClient(
            base_url=connection.datapoint_base_url, token=token, verify_ssl=connection.verify_ssl
        )

        new_id = uuid.uuid4()
        request = DataPointRequest(name=name, description="", existence=EnDataPointExistenceDTO.FULL, tags=tags)
        if connection.id_token:
            response = data_point_create_data_point.sync(data_point_id=str(new_id), client=client, json_body=request)
        else:
            response = data_point_create_data_point_2.sync(
                client=client, data_point_id=str(new_id), tenant_name=connection.tenant_name, json_body=request
            )

        if isinstance(response, ProblemDetails):
            log.error(response)
            return None

        data_point = cls(connection=connection, data_point_id=new_id, name=name)
        return data_point

    def __init__(self, connection: GnistaConnection, data_point_id: uuid.UUID, name: str = None):
        self.connection = connection
        self.data_point_id = data_point_id
        if name is None:
            self._load_details()
        else:
            self.name = name

    def __str__(self):
        return "GnistaDataPoint " + self.data_point_id + " with name " + self.name

    def _load_details(self):
        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datapoint_base_url, token=token, verify_ssl=self.connection.verify_ssl
        )
        if self.connection.id_token:
            data_point = data_point_get_data_point.sync(client=client, data_point_id=self.data_point_id)
        else:
            data_point = data_point_get_data_point_2.sync(
                client=client,
                data_point_id=self.data_point_id,
                tenant_name=self.connection.tenant_name,
            )
        if data_point is None:
            raise Exception("Cannot load Datapoint")
        self.name = data_point.name

    # pylint: disable=too-many-arguments
    def get_data_point_data(
        self,
        request: GetDataRequest,
        post_fix: bool = False,
    ) -> Union[List[DataFrame], float, Unset, None]:
        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datapoint_base_url, token=token, verify_ssl=self.connection.verify_ssl
        )

        if self.connection.id_token:
            byte_content = data_point_get_data.sync_detailed(
                client=client, data_point_id=str(self.data_point_id), json_body=request
            ).content
        else:
            byte_content = data_point_get_data_2.sync_detailed(
                client=client,
                data_point_id=str(self.data_point_id),
                tenant_name=self.connection.tenant_name,
                json_body=request,
            ).content

        log.debug("Received Response from gnista.io", content=byte_content)

        content_text = byte_content.decode("utf-8")
        jscon_content = json.loads(content_text)

        content_type = jscon_content["discriminator"]

        if content_type == "GetSeriesResponse":

            series_response = GetSeriesResponse.from_dict(jscon_content)
            curves = series_response.curves

            if isinstance(curves, list):
                data_frames = []
                # pylint: disable=E1133
                for curve in curves:
                    # pylint: enable=E1133
                    curve_dict = curve.curve
                    if isinstance(curve_dict, TimeSeriesResponseCurve):
                        data_frame = self._from_time_frames(time_frames=curve_dict.to_dict(), post_fix=post_fix)
                        data_frames.append(data_frame)

                return data_frames

        if content_type == "GetConstantResponse":
            constant_response = GetConstantResponse.from_dict(jscon_content)
            if constant_response is not None:
                return constant_response.value

        return None

    def append_data_point_data(
        self,
        data: Union[List[DataFrame], float],
        unit: Union[str, None],
    ) -> Union[Response[Union[Any, ProblemDetails]], None]:
        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datapoint_base_url, token=token, verify_ssl=self.connection.verify_ssl
        )

        if isinstance(data, list):
            sub_series: List[SubSeriesRequest] = []
            for data_frame in data:
                data_dict = self._to_dict(data_frame)
                value = SubSeriesRequestValues.from_dict(src_dict=data_dict)
                request = SubSeriesRequest(values=value)
                sub_series.append(request)

            append_request = AppendTimeSeriesRequest(sub_series=sub_series, unit=unit, part_id=str(uuid.uuid4()))

            if self.connection.id_token:
                return data_point_append_time_series_data.sync_detailed(
                    client=client, data_point_id=str(self.data_point_id), json_body=append_request
                )

            return data_point_append_time_series_data_2.sync_detailed(
                tenant_name=self.connection.tenant_name,
                client=client,
                data_point_id=str(self.data_point_id),
                json_body=append_request,
            )

        return None

    def set_data_point_data(
        self,
        data: Union[List[DataFrame], float],
        unit: Union[str, None],
        execution_id: Union[str, None],
    ) -> Union[Response[Union[Any, ProblemDetails]], None]:
        token = self.connection.get_access_token()
        client = AuthenticatedClient(
            base_url=self.connection.datapoint_base_url, token=token, verify_ssl=self.connection.verify_ssl
        )

        if isinstance(data, list):
            sub_series: List[SubSeriesRequest] = []
            for data_frame in data:
                data_dict = self._to_dict(data_frame)
                value = SubSeriesRequestValues.from_dict(src_dict=data_dict)
                request = SubSeriesRequest(values=value)
                sub_series.append(request)

            update_request = UpdateTimeSeriesRequest(sub_series=sub_series, unit=unit, execution_id=execution_id)

            if self.connection.id_token:
                return data_point_update_time_series_data.sync_detailed(
                    client=client, data_point_id=str(self.data_point_id), json_body=update_request
                )

            return data_point_update_time_series_data_2.sync_detailed(
                tenant_name=self.connection.tenant_name,
                client=client,
                data_point_id=str(self.data_point_id),
                json_body=update_request,
            )

        if isinstance(data, float):
            constant_request = UpdateConstantDataRequest(
                value=data,
                unit=unit,
                execution_id=execution_id,
            )
            if self.connection.id_token:
                return data_point_update_constant_data.sync_detailed(
                    client=client,
                    data_point_id=str(self.data_point_id),
                    json_body=constant_request,
                )

            return data_point_update_constant_data_2.sync_detailed(
                tenant_name=self.connection.tenant_name,
                client=client,
                data_point_id=str(self.data_point_id),
                json_body=constant_request,
            )

        return None

    def _to_dict(self, data_frame: DataFrame):
        result = {}
        dct = data_frame.to_dict()[self.VALUE_NAME]
        for key in dct.keys():
            value = dct[key]
            key_string = key.strftime(self.DATE_FORMAT)
            result[key_string] = value
        return result

    def _from_time_frames(self, time_frames: dict, post_fix: bool, date_format: str = DATE_FORMAT) -> DataFrame:

        if not isinstance(time_frames, dict):
            raise TypeError

        value_column_name = self.name

        if value_column_name is None:
            value_column_name = self.VALUE_NAME

        if post_fix:
            value_column_name = value_column_name + "_gnista.io_" + str(self.data_point_id)

        log.debug("Reading data as Pandas DataFrame")

        data_record = []
        for date in time_frames:
            value = time_frames[date]
            data_record.append({self.DATE_NAME: date, value_column_name: value})

        data_frame = pd.DataFrame.from_records(data_record, columns=[self.DATE_NAME, value_column_name])

        data_frame[self.DATE_NAME] = pd.to_datetime(data_frame[self.DATE_NAME], format=date_format)

        data_frame[value_column_name] = pd.to_numeric(data_frame[value_column_name])

        data_frame = data_frame.set_index(data_frame[self.DATE_NAME])
        data_frame = data_frame.drop([self.DATE_NAME], axis=1)

        return data_frame
