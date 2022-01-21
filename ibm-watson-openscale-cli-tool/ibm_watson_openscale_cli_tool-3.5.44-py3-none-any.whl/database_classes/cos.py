# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

# coding=utf-8
from ibm_botocore.client import Config
import ibm_boto3
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
import uuid
import time

logger = FastpathLogger(__name__)

BUCKET_NAME_PREFIX = 'wos-expresspath-bucket-'

class CloudObjectStorage():

    # IAM_STAGING_ENDPOINT = "https://iam.test.cloud.ibm.com/identity/token"
    # COS_STAGING_ENDPOINT = "https://s3.us-west.cloud-object-storage.test.appdomain.cloud"
    # IAM_PRODUCTION_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"
    # COS_PROD_ENDPOINT = "https://s3.us.cloud-object-storage.appdomain.cloud"

    def __init__(self, credentials, iam_url, cos_url):
        cos_url = cos_url[0] if type(cos_url) is tuple else cos_url
        self._cos = ibm_boto3.resource(
            's3',
            ibm_api_key_id=credentials['apikey'],
            ibm_service_instance_id=credentials['resource_instance_id'],
            ibm_auth_endpoint=iam_url,
            config=Config(signature_version='oauth'),
            endpoint_url=cos_url
        )

    def _get_existing_buckets(self):
        try:
            logger.log_debug("Retrieving list of existing buckets from IBM Cloud Object Storage ...")
            return self._cos.buckets.all()
        except Exception as e:
            logger.log_exception("Unable to retrieve list buckets: {}".format(str(e)))

    def get_wos_bucket(self):
        buckets = self._get_existing_buckets()
        for bucket in buckets:
            if bucket.name.startswith(BUCKET_NAME_PREFIX):
                logger.log_info("Found bucket: {}".format(bucket.name))
                return bucket
        return None

    def create_wos_bucket(self):
        bucket_name = BUCKET_NAME_PREFIX + str(uuid.uuid4())
        logger.log_info("Creating new bucket: {}".format(bucket_name))
        try:
            result = self._cos.Bucket(bucket_name).create()
            logger.log_info("Bucket: {} created".format(bucket_name))
            return result
        except Exception as e:
            logger.log_exception("Unable to create bucket: {}".format(str(e)))

    def delete_item(self, bucket_name, item_name):
        try:
            logger.log_info("Deleting item: {} from bucket: {}".format(item_name, bucket_name))
            self._cos.Object(bucket_name, item_name).delete()
            logger.log_info("Deleted item: {}".format(item_name))
        except Exception as e:
            logger.log_exception("Unable to delete item: {}".format(str(e)))

    def multi_part_upload(self, bucket_name, item_name, file_path_w_name):
        try:
            logger.log_info("Uploading item: {} to bucket: {}".format(item_name, bucket_name))
            # set 5 MB chunks and threadhold to 15 MB
            part_size = 1024 * 1024 * 5
            file_threshold = 1024 * 1024 * 15
            transfer_config = ibm_boto3.s3.transfer.TransferConfig(
                multipart_threshold=file_threshold,
                multipart_chunksize=part_size
            )
            with open(file_path_w_name, "rb") as file_data:
                self._cos.Object(bucket_name, item_name).upload_fileobj(
                    Fileobj=file_data,
                    Config=transfer_config
                )
            logger.log_info("Uploaded: {}".format(item_name))
        except Exception as e:
            logger.log_exception("Unable to upload item: {}".format(str(e)))

    def get_file(self, path):
        (bucket_name, file_name) = path.split('/')
        try:
            start = time.time()
            cos_object = self._cos.Object(bucket_name, file_name).get()
            cos_file = cos_object["Body"].read().decode('utf-8')
            elapsed = time.time() - start
            logger.log_timer('cos.Object.get.read.decode {} in {:.3f} seconds'.format(path, elapsed))
        except Exception as e:
            error_msg = 'Unable to read file from IBM Cloud Object Storage: {}'.format(str(e))
            logger.log_exception(error_msg)
            raise Exception(error_msg)
        return cos_file
