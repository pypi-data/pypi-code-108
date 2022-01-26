# !/usr/bin/env python
# -*- coding:utf-8 -*-
""" 
@author: Wang Ye (Wayne)
@file: ocs_api.py
@time: 2021/10/08
@contact: wangye@oppo.com
@site: 
@software: PyCharm
# code is far away from bugs.
"""

import boto3
from botocore.exceptions import ClientError
import logging


class OCS:
    def __init__(self, access_key, secret_key, endpoint, region, bucket_name):
        self.ak = access_key
        self.sk = secret_key
        self.endpoint = endpoint
        self.region = region
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.ak,
            aws_secret_access_key=self.sk,
            endpoint_url=endpoint,
            region_name=region,
            use_ssl=False
        )
        # boto3.set_stream_logger(name='', level=logging.DEBUG)

    def put_object(self, in_path: str, key: str):
        """
        Adds an object to a bucket.
        refer to https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.put_objectse
        """
        try:
            with open(in_path, 'rb') as f:
                resp = self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=f
                )
                logging.debug(resp)
        except ClientError as e:
            if e.response['ResponseMetadata']['HTTPStatusCode'] // 100 == 4:
                logging.error('client error with invalid parameter')
            elif e.response['ResponseMetadata']['HTTPStatusCode'] // 100 == 5:
                logging.error('ocs server internal error')
            else:
                logging.error('other ocs errors')
            logging.error(e.response)

        except Exception as e:  # other errors such as network io
            logging.error('other error such as network io:' + str(e))

    def get_object(self, out_path: str, key: str):
        """
        Retrieves objects from OCS
        refer to https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.get_object
        """
        try:
            resp = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            body = resp["Body"]
            with open(out_path, 'wb') as f:
                for chunk in body:
                    f.write(chunk)
        except ClientError as e:
            if e.response['ResponseMetadata']['HTTPStatusCode'] // 100 == 4:
                logging.error('client error with invalid parameter')
            elif e.response['ResponseMetadata']['HTTPStatusCode'] // 100 == 5:
                logging.error('ocs server internal error')
            else:
                logging.error('other ocs errors')
            logging.error(e.response)

        except Exception as e:  # other errors such as network io
            logging.error('other error such as network io:' + str(e))

    def delete_object(self, key):
        """The DELETE operation remove the object storage in OCS.

        refer to https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_object
        """
        try:
            resp = self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key,
            )
            logging.debug(resp)

        except ClientError as e:
            if e.response['ResponseMetadata']['HTTPStatusCode'] // 100 == 4:
                logging.error('client error with invalid parameter')
            elif e.response['ResponseMetadata']['HTTPStatusCode'] // 100 == 5:
                logging.error('ocs server internal error')
            else:
                logging.error('other ocs errors')
            logging.error(e.response)

        except Exception as e:  ## other errors such as network io
            logging.error('other error such as network io:' + str(e))

    def list_objects(self):
        """
        Returns some or all of the objects in a bucket.
         You can use the request parameters as selection criteria to return a subset of the objects in a bucket.
         refer to https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.list_objects
        """
        objects = []
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                MaxKeys=5,  # list up to 5 key at a time
            )
            objects.append(response['Contents'])
            while response['IsTruncated']:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    StartAfter=response['Contents'][-1]['Key']
                )
                objects.append(response['Contents'])

            # pprint.pprint(objects)
            return objects

        except ClientError as e:
            if e.response['ResponseMetadata']['HTTPStatusCode'] // 100 == 4:
                logging.error('client error with invalid parameter')
            elif e.response['ResponseMetadata']['HTTPStatusCode'] // 100 == 5:
                logging.error('ocs server internal error')
            else:
                logging.error('other ocs errors')
            logging.error(e.response)

        except Exception as e:  # other errors such as network io
            logging.error('other error such as network io:' + str(e))

    def list_prefix(self, prefix: str):
        try:
            ret = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)['Contents']
        except ClientError:
            # Not found
            ret = []
        return ret

    def has_prefix(self, prefix: str):
        return 'Contents' in self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix, MaxKeys=1)

    def has_key(self, key: str):
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
        except ClientError as e:
            return int(e.response['Error']['Code']) != 404
        return True


def get_ocs_obj(env='test', bucket='ntt'):
    if env not in ('test', 'prod'): return None
    if bucket == 'ntt':
        return OCS(
            access_key='cWKJwKy-NaghHT47qgK0MCci6nHOSyhNfLEiMGQ9',
            secret_key='Ow7dXEBDrqtBE4V8y7NcXB_rq49hVXxVw0jw5fCG',
            endpoint='https://ocs-cn-south1.heytapcs.com',
            region='cn-south-1',
            bucket_name=f'health-data-store-{env}'
        )
    elif bucket == 'wayne':
        return OCS(
            access_key='3REgcFTraVZWp5JStmUr1bESMVoZFCaDW_hlAa39',
            secret_key='-36Si3hT5VptlFHEQy78ZkKgYlStzcwuY1m5Goz0',
            endpoint='https://ocs-cn-south1.heytapcs.com',
            region='cn-south-1',
            bucket_name='bucket-test'
        )


if __name__ == '__main__':
    ocs_agent = get_ocs_obj('test', 'wayne')
    ocs_agent.delete_object('debug/hr/a.jpg')
