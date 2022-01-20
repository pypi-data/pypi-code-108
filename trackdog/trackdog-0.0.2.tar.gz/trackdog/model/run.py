class Run(object):
    def __init__(self, name=None, project=None):
        self.name = name
        self.project = project
        self.metrics = []
    
    def add_metric(self, metric):
        self.metrics = self.metrics + [metric]
