import enum
from mc_automation_tools import common


class S3Provider:
    """This class provide s3 credential """
    def __init__(self, entrypoint_url, access_key, secret_key, bucket_name=None):
        self.s3_entrypoint_url = entrypoint_url
        self.s3_access_key = access_key
        self.s3_secret_key = secret_key
        self.s3_bucket_name = bucket_name

    def get_entrypoint_url(self):
        return self.s3_entrypoint_url

    def get_access_key(self):
        return self.s3_access_key

    def get_secret_key(self):
        return self.s3_secret_key

    def get_bucket_name(self):
        return self.s3_bucket_name


class ResponseCode(enum.Enum):
    """
    Types of server responses
    """
    Ok = 200  # server return ok status
    ChangeOk = 201  # server was return ok for changing
    NoJob = 204  # No job
    ValidationErrors = 400  # bad request
    StatusNotFound = 404  # status\es not found on db
    DuplicatedError = 409  # in case of requesting package with same name already exists
    GetwayTimeOut = 504  # some server didn't respond
    ServerError = 500  # problem with error


class JobStatus(enum.Enum):
    """
    Types of job statuses
    """
    Completed = 'Completed'
    Failed = 'Failed'
    InProgress = 'In-Progress'
    Pending = 'Pending'


class MapProtocolType(enum.Enum):
    """
    Types of orthophoto access protocol statuses
    """
    WMS = 'WMS'
    WMTS = 'WMTS'



job_ingestion_type = 'Discrete-Tiling'
S3_DOWNLOAD_EXPIRATION_TIME = common.get_environment_variable("S3_DOWNLOAD_EXPIRED_TIME", 3600)
CERT_DIR = common.get_environment_variable('CERT_DIR', None)
CERT_DIR_GQL = common.get_environment_variable('CERT_DIR_GQL', None)

JOB_TASK_QUERY = """
query jobs ($params: JobsSearchParams){
  jobs(params: $params) {
                id
                resourceId
                version
                isCleaned
                status
                reason
                type
                created
                id
    			tasks {
                id
                status
              			}
  						 }	
										}
"""

# mapping of zoom level and related resolution values
zoom_level_dict = {
    0: 0.703125,
    1: 0.3515625,
    2: 0.17578125,
    3: 0.087890625,
    4: 0.0439453125,
    5: 0.02197265625,
    6: 0.010986328125,
    7: 0.0054931640625,
    8: 0.00274658203125,
    9: 0.001373291015625,
    10: 0.0006866455078125,
    11: 0.00034332275390625,
    12: 0.000171661376953125,
    13: 0.0000858306884765625,
    14: 0.0000429153442382812,
    15: 0.0000214576721191406,
    16: 0.0000107288360595703,
    17: 0.00000536441802978516,
    18: 0.00000268220901489258,
    19: 0.00000134110450744629,
    20: 0.000000670552253723145,
    21: 0.000000335276126861572,
    22: 0.000000167638063430786
}
