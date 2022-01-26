from io import StringIO
import pandas as pd
from time import sleep
from typing import Optional, List, Union, Callable
from tim.core import Credentials
from tim.core.api import execute_request
from tim.core.credentials import Credentials
from tim.types import ExecuteResponse, Logs, Status, StatusResponse
from .types import BuildModelResponse, ForecastAccuracies, ForecastModelResult, ForecastJobConfiguration, ForecastMetadata, ForecastTableRequestPayload


def build_model(credentials: Credentials, job_configuration: ForecastJobConfiguration) -> BuildModelResponse:
  return execute_request(
      credentials, method='post', path='/forecast-jobs/build-model', body=job_configuration
  )


def execute(credentials: Credentials, id: str) -> ExecuteResponse:
  return execute_request(credentials=credentials, method='post', path=f'/forecast-jobs/{id}/execute')


def get_status(credentials: Credentials, id: str) -> StatusResponse:
  return execute_request(credentials=credentials, method='get', path=f'/forecast-jobs/{id}/status')


def get_forecast(credentials: Credentials, id: str) -> ForecastMetadata:
  return execute_request(credentials=credentials, method='get', path=f'/forecast-jobs/{id}')


def get_forecasting_jobs(
    credentials: Credentials,
    offset: Union[int, None] = None,
    limit: Union[int, None] = None,
    sort: Union[str, None] = None,
    experiment_id: Union[str, None] = None,
    use_case_id: Union[str, None] = None,
    type: Union[str, None] = None,
    status: Union[str, None] = None,
    parent_id: Union[str, None] = None,
    from_datetime: Union[str, None] = None,
    to_datetime: Union[str, None] = None
) -> List[ForecastMetadata]:
  payload = {
      "experimentId": experiment_id,
      "useCaseId": use_case_id,
      "sort": sort,
      "type": type,
      "status": status,
      "parentId": parent_id,
      "from": from_datetime,
      "to": to_datetime,
      "limit": limit,
      "offset": offset
  }

  return execute_request(credentials=credentials, method='get', path=f'/forecast-jobs', params=payload)


def get_forecast_table_results(
    credentials: Credentials, id: str, forecastType: Optional[str] = None, modelIndex: Optional[int] = None
) -> pd.DataFrame:
  payload = ForecastTableRequestPayload(forecastType=forecastType, modelIndex=modelIndex)

  response = execute_request(
      credentials=credentials, method='get', path=f'/forecast-jobs/{id}/results/table', params=payload
  )

  data_string = StringIO(response)

  return pd.read_csv(data_string)  # pyright: reportGeneralTypeIssues=false, reportUnknownMemberType=false


def get_forecast_model_results(credentials: Credentials, id: str) -> ForecastModelResult:
  return execute_request(credentials=credentials, method='get', path=f'/forecast-jobs/{id}/results/model')


def get_forecast_accuracies_result(credentials: Credentials, id: str) -> ForecastAccuracies:
  return execute_request(
      credentials=credentials, method='get', path=f'/forecast-jobs/{id}/results/accuracies'
  )


def get_forecast_logs(credentials: Credentials, id: str) -> List[Logs]:
  return execute_request(credentials=credentials, method='get', path=f'/forecast-jobs/{id}/log')


def poll_forecast_status(
    credentials: Credentials,
    id: str,
    handle_status_poll: Optional[Callable[[StatusResponse], None]] = None,
    tries_left: int = 150
) -> StatusResponse:
  if tries_left < 1:
    raise ValueError("Timeout error.")

  response = get_status(credentials, id)
  if handle_status_poll: handle_status_poll(response)

  if Status(response['status']).value == Status.FAILED.value:
    return response
  if Status(response['status']).value != Status.FINISHED.value and Status(
      response['status']
  ).value != Status.FINISHED_WITH_WARNING.value:
    sleep(2)
    return poll_forecast_status(credentials, id, handle_status_poll, tries_left - 1)

  return response


def delete_forecast(credentials: Credentials, id: str) -> ExecuteResponse:
  return execute_request(credentials=credentials, method="delete", path=f"/forecast-jobs/{id}")
