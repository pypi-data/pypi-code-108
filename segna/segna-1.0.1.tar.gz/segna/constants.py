BASE_URL = 'https://backend.segna.io/server-side'

class API:
    RUN_JOB = '/run-job'
    JOB_DATA = '/job-data'


class Request:
    DATA_TYPE = 'dataType'

    class DataTypeFormats:
        DATAFRAME = 'dataframe'


class Response:
    JOB_ID = 'jobId'
    DATA = 'data'
    ERROR = 'errorMessage'
    DATA_TYPES = 'dtypes'

