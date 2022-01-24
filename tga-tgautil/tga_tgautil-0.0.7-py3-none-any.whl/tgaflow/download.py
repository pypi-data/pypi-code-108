from tgaflow.base import BaseTask
from tgautil.download_util import DownloadUtil
from tgautil.sql_format import SQLFormat
from tgautil.dingtalk import send_dingtalk_message
import time
import logging
logger = logging.getLogger('task')


class DownloadTask(BaseTask):
    def __init__(self, flow_id, params):
        self.task_name = 'download'
        super().__init__(flow_id, params, ['check', 'refresh'])

    def process(self):
        sqlFormat = SQLFormat()
        du = DownloadUtil({
            'name': self.params['name'],
            'sql': sqlFormat.run(self.params)

        })
        filepath = None
        try_num = 0

        while (not filepath) and try_num <= 3:
            try:
                filepath = du.run()
            except Exception as e:
                try_num = try_num + 1
                if try_num <= 3:
                    logger.info(' DownloadTask flow_id: %s . exception: %s . try num: %s ', self.flow_id, e, try_num)
                    time.sleep(3)
                else:
                    logger.error(' DownloadTask flow_id: %s . error: %s . try num: %s ', self.flow_id, e, try_num - 1)
                    send_dingtalk_message(
                        f' DownloadTask flow_id: {self.flow_id} . error: {e} . try num: {try_num - 1} ')
                    return

        if filepath is None:
            return False, {'result': filepath}
        else:
            return True, {'filepath': filepath}
