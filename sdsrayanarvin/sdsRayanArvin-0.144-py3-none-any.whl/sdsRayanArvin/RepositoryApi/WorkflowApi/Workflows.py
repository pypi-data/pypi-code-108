from sdsRayanArvin.Dataset.WorkflowsData import WorkflowsData
from sdsRayanArvin.Repository import Repository


class Workflows(Repository):
    def dataAll(self):
        res = self.Request.sendWithToken('GET', 'workflow_data')
        try:
            workflows = []
            for workflow in res['success']:
                workflows.append(WorkflowsData(workflow).data)
            return workflows
        except:
            return []

    def dataOnID(self, ID_workflows):
        res = self.Request.sendWithToken('GET', 'workflow_data/' + ID_workflows)
        try:
            return WorkflowsData(res['success']).data
        except:
            return []
