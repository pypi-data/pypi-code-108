# TODO(gaocegege): Make it extensible to other platforms.
class Metric(object):
    def __init__(self, name=None, project=None, run=None):
        self.name = name
        self.project = project
        self.run = run
        # TODO(gaocegege): Keep it more efficient.
        self.datapoints = []
    
    def add_datapoint(self, dp):
        # TODO(gaocegege): Support epoch and step.
        self.datapoints = self.datapoints + [dp]
