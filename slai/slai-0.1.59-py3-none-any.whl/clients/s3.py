import boto3

from slai.exceptions import InvalidAWSProfile
from botocore.exceptions import ClientError, ProfileNotFound
from slai.modules.parameters import from_config
from importlib import import_module


def get_s3_client(*, aws_profile, region):
    import_path = from_config(
        "S3_CLIENT",
        "slai.clients.S3_CLIENT",
    )
    class_ = import_path.split(".")[-1]
    path = ".".join(import_path.split(".")[:-1])
    return getattr(import_module(path), class_)(aws_profile, region)


class S3Client:
    def __init__(self, *, aws_profile, aws_region):
        try:
            self.session = boto3.Session(
                profile_name=aws_profile, region_name=aws_region
            )
        except ProfileNotFound:
            raise InvalidAWSProfile("profile_not_found")

        self.aws_region = aws_region
        self.client = self.session.client("s3")

    def create_bucket(self, bucket_name, aws_region=None):
        try:
            self.client.create_bucket(Bucket=bucket_name)
        except ClientError:
            raise

        return True

    def upload(
        self, *, bucket_name, data, key, content_type="application/octet-stream"
    ):
        try:
            object = self.client.Object(
                bucket_name,
                key,
            )
            response = object.put(Body=data, ContentType=content_type)
            print("successfully uploaded file: {}".format(response))
        except ClientError as e:
            print(str(e))

        return response

    # def read_file(self, *, key):
    #     file_stream = None

    #     try:
    #         object = self.client.Object(
    #             S3_BUCKET_NAME,
    #             key,
    #         )
    #         file_stream = object.get()["Body"].read()

    #     except ClientError as e:
    #         print(str(e))

    #     return file_stream
