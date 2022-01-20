from urllib import request


class BaseMonitoringTest():
    response = None

    def check(self):
        return True


# Django tests
class BaseDataBaseMonitoringTest(BaseMonitoringTest):
    cls = None

    def __init__(self, cls):
        self.cls = cls

    def check(self):
        try:
            return len(self.cls.objects.all()) >= 0
        except Exception as e:
            self.response = f'BaseDataBaseMonitoringTest Error {str(e)}'
            return False


# AWS internal services tests
class BaseElasticacheMonitoringTest(BaseMonitoringTest):
    django_rq = None

    def __init__(self, django_rq):
        self.django_rq = django_rq

    def check(self):
        try:
            self.django_rq.get_connection('default')
            return True
        except Exception as e:
            self.response = f'BaseElasticacheMonitoringTest Error {str(e)}'
            return False


class BaseKinesisMonitoringTest(BaseMonitoringTest):
    client = None
    stream_name = None

    def __init__(self, client, stream_name):
        self.client = client
        self.stream_name = stream_name

    def check(self):
        try:
            self.client.list_shards(
                StreamName=self.stream_name,
                MaxResults=1
            )
            return True
        except Exception as e:
            self.response = f'BaseKinesisMonitoringTest Error {str(e)}'
            return False


class BaseSQSMonitoringTest(BaseMonitoringTest):
    client = None
    queue_name = None

    def __init__(self, client, queue_name):
        self.client = client
        self.queue_name = queue_name

    def check(self):
        try:
            self.client.get_queue_by_name(self.queue_name)
            return True
        except Exception as e:
            self.response = f'BaseSQSMonitoringTest Error {str(e)}'
            return False


class BaseS3MonitoringTest(BaseMonitoringTest):
    client = None
    bucket_name = None

    def __init__(self, client, bucket_name):
        self.client = client
        self.bucket_name = bucket_name

    def check(self):
        try:
            self.client.Bucket(self.bucket_name)
            return True
        except Exception as e:
            self.response = f'BaseS3MonitoringTest Error {str(e)}'
            return False


# External services tests
class BaseAlgoliaMonitoringTest(BaseMonitoringTest):
    index = None

    def __init__(self, index):
        self.index = index

    def check(self):
        try:
            self.index.search('')
            return True
        except Exception as e:
            self.response = f'BaseAlgoliaMonitoringTest Error {str(e)}'
            return False


class BaseFirebaseMonitoringTest(BaseMonitoringTest):
    client = None

    def __init__(self, client):
        self.client = client

    def check(self):
        try:
            self.client.list_users(max_results=1)
            return True
        except Exception as e:
            self.response = f'BaseFirebaseMonitoringTest Error {str(e)}'
            return False


class BaseExternalUrlMonitoringTest(BaseMonitoringTest):
    url = None

    def __init__(self, url):
        self.url = url

    def check(self):
        try:
            status_code = request.urlopen(self.url).getcode()
            if status_code <= 299:
                return True
            self.response = 'BaseExternalUrlMonitoringTest Error: ' \
                            + f'Status code {status_code}'
            return False
        except Exception as e:
            self.response = f'BaseExternalUrlMonitoringTest Error {str(e)}'
            return False
