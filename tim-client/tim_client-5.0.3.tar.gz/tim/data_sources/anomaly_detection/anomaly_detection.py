from io import StringIO
import pandas as pd
from typing import Callable, List, Optional, Union
from time import sleep
from tim.types import ExecuteResponse, Logs, Status, StatusResponse
from tim.core.api import execute_request
from tim.data_sources.anomaly_detection.types import AnomalyDetectionJobModelResult, AnomalyDetection, BuildModelResponse, AnomalyDetectionJobConfiguration, AnomalyDetectionDetectConfiguration
from tim.core.credentials import Credentials


def build_model(
    credentials: Credentials, job_configuration: AnomalyDetectionJobConfiguration
) -> BuildModelResponse:
  return execute_request(
      credentials=credentials, method='post', path='/detection-jobs/build-model', body=job_configuration
  )


def detect(
    credentials: Credentials, parent_job_id: str,
    job_configuration: Union[AnomalyDetectionDetectConfiguration, None]
) -> BuildModelResponse:
  return execute_request(
      credentials=credentials,
      method='post',
      path=f'/detection-jobs/{parent_job_id}/detect',
      body=job_configuration
  )


def get_anomaly_detection_logs(credentials: Credentials, id: str) -> List[Logs]:
  return execute_request(credentials=credentials, method='get', path=f'/detection-jobs/{id}/log')


def execute_anomaly_detection(credentials: Credentials, id: str) -> ExecuteResponse:
  return execute_request(credentials=credentials, method='post', path=f'/detection-jobs/{id}/execute')


def get_anomaly_detection_job_status(credentials: Credentials, id: str) -> StatusResponse:
  return execute_request(credentials=credentials, method='get', path=f'/detection-jobs/{id}/status')


def get_anomaly_detection(credentials: Credentials, id: str) -> AnomalyDetection:
  return execute_request(credentials=credentials, method='get', path=f'/detection-jobs/{id}')


def get_anomaly_detection_jobs(
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
) -> List[AnomalyDetection]:
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

  return execute_request(credentials=credentials, method='get', path=f'/detection-jobs', params=payload)


def get_anomaly_detection_table_results(credentials: Credentials, id: str) -> pd.DataFrame:
  response = execute_request(
      credentials=credentials, method='get', path=f'/detection-jobs/{id}/results/table'
  )

  data_string = StringIO(response)

  return pd.read_csv(data_string)  # pyright: reportGeneralTypeIssues=false, reportUnknownMemberType=false


def get_anomaly_detection_model_results(credentials: Credentials, id: str) -> AnomalyDetectionJobModelResult:
  return execute_request(credentials=credentials, method='get', path=f'/detection-jobs/{id}/results/model')


def poll_anomaly_detection_status(
    credentials: Credentials,
    id: str,
    handle_status_poll: Optional[Callable[[StatusResponse], None]] = None,
    tries_left: int = 150
) -> StatusResponse:
  if tries_left < 1:
    raise ValueError("Timeout error.")

  response = get_anomaly_detection_job_status(credentials, id)
  if handle_status_poll: handle_status_poll(response)

  if Status(response['status']).value == Status.FAILED.value:
    return response
  if Status(response['status']).value != Status.FINISHED.value and Status(
      response['status']
  ).value != Status.FINISHED_WITH_WARNING.value:
    sleep(2)
    return poll_anomaly_detection_status(credentials, id, handle_status_poll, tries_left - 1)

  return response


def delete_anomaly_detection(credentials: Credentials, id: str) -> ExecuteResponse:
  return execute_request(credentials=credentials, method="delete", path=f"/detection-jobs/{id}")
