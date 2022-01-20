from rastless.db.handler import Database
from rastless.core.s3 import S3Bucket
from rastless import settings


class Cfg:
    def __init__(self, table_name, bucket_name):
        self.db = Database(table_name)
        self.s3 = S3Bucket(bucket_name)
