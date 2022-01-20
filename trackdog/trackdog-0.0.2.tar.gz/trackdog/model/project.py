# TODO(gaocegege): Make it extensible to other platforms.
class Project(object):
    def __init__(self, name=None):
        self.name = name
        self.runs = []
    
    def add_run(self, run):
        self.runs = self.runs + [run]
