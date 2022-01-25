import pandas as pd
import requests

import segna.constants as cst
from segna.job_config import JobConfig

SEGNA_ACCESS_KEY = None
SEGNA_SECRET_ACCESS_KEY = None


def init(access_key, secret_key):
    global SEGNA_ACCESS_KEY, SEGNA_SECRET_ACCESS_KEY
    SEGNA_ACCESS_KEY = access_key
    SEGNA_SECRET_ACCESS_KEY = secret_key


def configure_job(pipeline_id, job_name='temp_job') -> JobConfig:
    return JobConfig(pipeline_id, job_name)


def run_job(config_obj) -> str:
    if SEGNA_ACCESS_KEY is None or SEGNA_SECRET_ACCESS_KEY is None:
        raise ValueError('Please specify your access and secret key by calling segna.init')
    r = requests.post(cst.BASE_URL + cst.API.RUN_JOB,
                      json=config_obj.to_json(),
                      auth=(SEGNA_ACCESS_KEY, SEGNA_SECRET_ACCESS_KEY))
    r.raise_for_status()
    job_id = r.json()[cst.Response.JOB_ID]
    return job_id


def get_job_data(job_id) -> pd.DataFrame:
    payload = {cst.Request.DATA_TYPE: cst.Request.DataTypeFormats.DATAFRAME}
    r = requests.post(cst.BASE_URL + cst.API.JOB_DATA + f'/{job_id}',
                      auth=(SEGNA_ACCESS_KEY, SEGNA_SECRET_ACCESS_KEY),
                      params=payload)
    response_data = r.json()
    try:
        r.raise_for_status()
    finally:
        error_message = response_data.get(cst.Response.ERROR)
        if error_message:
            print("ERROR: " + error_message)

    list_data = response_data[cst.Response.DATA]
    dtypes = response_data[cst.Response.DATA_TYPES]
    columns = list_data.pop(0)
    data = pd.DataFrame(list_data, columns=columns)
    data = data.astype(dtypes)
    return data
