import boto3
import botocore


class S3Bucket:
    def __init__(self, bucketName, region, endpoint=None):
        s3 = boto3.resource('s3', region_name=region, endpoint_url=endpoint)
        self._bucket = s3.Bucket(bucketName)

    def download(self, objectKey, targetFileName=None):
        if targetFileName is None:
            targetFileName = objectKey

        try:
            self._bucket.download_file(objectKey, targetFileName)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise

    def upload(self, filename, objectKey=None):
        if objectKey is None:
            objectKey = filename

        try:
            self._bucket.upload_file(filename, objectKey)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("Could not upload the file.")
            else:
                raise

    def delete(self, objectKey):
        try:
            self._bucket.delete_object(objectKey)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise
