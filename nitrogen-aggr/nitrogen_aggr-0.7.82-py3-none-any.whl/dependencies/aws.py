import boto3
import json

from botocore.exceptions import ClientError

from dependencies.exception import exception_handler

class cadmium_aws:
    def __init__(self, _awskey=None, _awssecret=None):
        self.bucket_name = ""

    def s3_client(self):
        return boto3.client('s3')

    def s3_resource(self, _awskey=None, _awssecret=None):
        if _awskey is not None:
            return boto3.resource('s3',
                                  aws_access_key_id=_awskey,
                                  aws_secret_access_key=_awssecret)

        return boto3.resource('s3')

    def read_json_from_bucket(self, bucket_name, target_file, _awskey=None, _awssecret=None):
        if _awskey is not None:
            try:
                s3 = self.s3_resource(_awskey=_awskey, _awssecret=_awssecret)
                config_s3 = s3.Object(bucket_name, target_file)
                config_raw = config_s3.get()['Body'].read().decode('utf-8')
                s3_client_json = json.loads(config_raw)
                return s3_client_json

            except ClientError as e:
                print("Unexpected error: %s" % e)
                print(f'No such file {target_file}')
                return 0

        try:
            s3_client_obj = self.s3_client().get_object(Bucket=bucket_name, Key=target_file)
            s3_client_data = s3_client_obj['Body'].read().decode('utf-8')
            s3_client_json = json.loads(s3_client_data)
            return s3_client_json

        except ClientError as e:
            print("Unexpected error: %s" % e)
            print(f'No such file {target_file}')
            return 0

    def write_json_to_bucket(self, json_val,  bucket_name, target_file, _awskey=None, _awssecret=None):
        if _awskey is not None:
            try:
                s3 = self.s3_resource(_awskey=_awskey, _awssecret=_awssecret)
                return s3.Object(
                    bucket_name,
                    target_file
                ).put(
                    Body=json_val.encode('utf-8')
                )

            except ClientError as e:
                print("Unexpected error: %s" % e)
                print(f'No such file {target_file}')
                return 0

        try:


            return self.s3_client().put_object(
                Body=json_val,
                Bucket=bucket_name,
                Key=target_file
            )

        except ClientError as e:
            print("Unexpected error: %s" % e)
            print(f'No such file {target_file}')
            return 0