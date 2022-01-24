from tgaflow.base import BaseTask


class TransferBaseTask(BaseTask):
    def __init__(self, flow_id, params):
        self.task_name = 'transfer'
        super().__init__(flow_id, params, ['download'])

    def process(self):
        pass