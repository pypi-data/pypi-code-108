import json
import logging

from config.settings import TGA
from proj.models import CeleryTask
from tgautil.dingtalk import send_dingtalk_message

logger = logging.getLogger('task')


class BaseTask:
    def __init__(self, flow_id, params, depends=[]):
        # 接收参数
        self.flow_id = flow_id
        self.params = params
        self.depends = depends

        if 'depends' in self.params:
            self.depends = self.params['depends']

        self.run_status = 0  # 0 不可执行 1 可执行
        # 读取配置
        self.settings = TGA

        self.task, _ = CeleryTask.objects.get_or_create(flow_id=flow_id, task_name=self.task_name)

        if self.task.status == 1:
            self.run_status = 0
        else:
            depend_success_count = CeleryTask.objects.filter(flow_id=flow_id, task_name__in=self.depends,
                                                             status=2).count()
            if depend_success_count == len(self.depends):
                self.run_status = 1

    def handle(self):
        if self.task.status == 2:
            return True
        if self.run_status != 1:
            logger.info('cant run: %s, %s', self.flow_id, self.run_status)
            return False
        # process 由子类继承，必须返回true or false
        CeleryTask.objects.filter(flow_id=self.flow_id, task_name=self.task_name).update(status=1)
        success, result = self.process()
        if success:
            CeleryTask.objects.filter(flow_id=self.flow_id, task_name=self.task_name).update(status=2, result=result)
        else:
            send_dingtalk_message(json.dumps({'result': result, 'flow_id': self.flow_id, 'params': self.params}))
            CeleryTask.objects.filter(flow_id=self.flow_id, task_name=self.task_name).update(status=0, result=result)

    def process(self):
        pass
