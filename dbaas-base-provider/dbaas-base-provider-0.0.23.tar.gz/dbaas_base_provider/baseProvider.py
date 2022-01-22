from time import sleep
from socket import timeout

from .base import BaseProviderObject
from .base import MongoClient


class BaseProvider(BaseProviderObject):
    SECONDS_OPERATION_RETRY = 3
    MAX_OPERATION_RETRY = SECONDS_OPERATION_RETRY * 1000

    def __init__(self, environment, engine=None, auth_info=None):
        super(BaseProvider, self).__init__()
        self.environment = environment
        self._client = None
        self._credential = None
        self._commands = None
        self.engine = engine
        self.auth_info = auth_info

    @property
    def client(self):
        if not self._client:
            self._client = self.build_client()
        return self._client

    @property
    def credential(self):
        if not self._credential:
            self._credential = self.build_credential()
        return self._credential

    def credential_add(self, content):
        credential_cls = self.get_credential_add()
        credential = credential_cls(self.provider, self.environment, content)

        is_valid, error = credential.is_valid(content)
        if not is_valid:
            return False, error

        try:
            insert = credential.save()
        except Exception as e:
            return False, str(e)
        else:
            return True, insert.get('_id')

    def build_client(self):
        raise NotImplementedError

    def build_credential(self):
        raise NotImplementedError

    def get_credential_add(self):
        raise NotImplementedError

    def get_or_none_resource(self, operation, **kw):
        try:
            response = operation().get(**kw).execute()
        except Exception as ex:
            if ex.resp.status == 404:
                return None
            raise Exception(ex)

        return response

    @classmethod
    def get_provider(cls):
        raise NotImplementedError

    @property
    def provider(self):
        return self.get_provider()

    def wait_operation(self, operation=None, region=None, zone=None):
        op = self._wait(
            operation=operation,
            region=region,
            zone=zone
        )
        return self._check_operation_status(op)

    def _wait(self, operation, region=None, zone=None):
        if not operation:
            raise EnvironmentError('operation must be provided')

        retry = 0
        if zone:
            op = self._get_wait_zone_operation(
                zone=zone,
                operation=operation
            )
        elif region:
            op = self._get_wait_region_operation(
                region=region,
                operation=operation
            )
        else:
            op = self._get_wait_global_operation(
                operation=operation
            )

        while retry <= self.MAX_OPERATION_RETRY:
            try:
                operation = op.execute()
            except Exception as ex:
                if isinstance(ex, timeout):
                    sleep(self.SECONDS_OPERATION_RETRY)
                    retry += 1
                else:
                    raise Exception(ex)
            else:
                return operation

        raise EnvironmentError('Error while wait %s operation' % operation)

    def _get_wait_zone_operation(self, zone, operation, execute_request=False):
        operation = self.client.zoneOperations().wait(
            project=self.credential.project,
            zone=zone,
            operation=operation
        )

        if execute_request:
            return operation.execute()

        return operation

    def _get_wait_region_operation(self, region, operation,
                                   execute_request=False):
        operation = self.client.regionOperations().wait(
            project=self.credential.project,
            region=region,
            operation=operation
        )

        if execute_request:
            return operation.execute()

        return operation

    def _get_wait_global_operation(self, operation, execute_request=False):
        operation = self.client.globalOperations().wait(
            project=self.credential.project,
            operation=operation
        )

        if execute_request:
            return operation.execute()

        return operation

    def _check_operation_status(self, operation):
        if operation.get('error'):
            error = 'Error in {} operation: {}'.format(
                operation.get('operationType'),
                operation.get('error')
            )
            raise Exception(error)

        if operation.get('status') != 'DONE':
            error = 'Operation {} is not Done. Status: {}'.format(
                operation.get('operationType'),
                operation.get('status')
            )
            raise Exception(error)

        return True
