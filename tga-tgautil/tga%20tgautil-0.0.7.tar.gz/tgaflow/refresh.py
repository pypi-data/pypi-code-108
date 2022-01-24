import json
import logging
import requests
from proj.celery import app
from tgaflow.base import BaseTask

logger = logging.getLogger('task')


class RefreshTask(BaseTask):
    def __init__(self, flow_id, params):
        self.task_name = 'refresh'
        super().__init__(flow_id, params, [])
        self.url = self.settings['base_url'] + '/open/user-cluster-refresh'

    def process(self):
        try:
            result = requests.post(self.url, headers={
                'Content-Type': 'application/json',
            }, params={
                ('token', self.settings['token']),
                ('projectId', self.params['projectId']),
                ('clusterId', self.params['clusterId']),
            }, timeout=300)
            logger.info('refreshtask success: %s' % result.text)
            resultArr = json.loads(result.text)
            if 'return_code' in resultArr and resultArr['return_code'] != 0:
                return False, {'result': result.text}
            return True, {}
        except Exception as e:
            logger.info('refreshtask error: %s' % e)
            return False, {'result': str(e)}
