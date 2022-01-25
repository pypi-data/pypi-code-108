BASE_URL = 'https://backend.segna.io/public/server-side'


class API:
    RUN_JOB = '/v1/run-job'
    JOB_DATA = '/v1/job-data'


class Request:
    DATA_TYPE = 'dataType'

    class DataTypeFormats:
        DATAFRAME = 'dataframe'


class Response:
    JOB_ID = 'jobId'
    DATA = 'data'
    ERROR = 'errorMessage'
    DATA_TYPES = 'dtypes'

