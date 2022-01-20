import logging


class Getter(object):
    def __init__(self, store):
        self.logger = logging.getLogger(__name__)
        self.store = store

    def get(self, resource, *names):
        if resource == "project":
            return self.store.get_projects(names[0])
        elif resource == "run":
            # TODO(gaocegege): Support project name.
            return self.store.get_runs(None, names[0])
        elif resource == "metric":
            return self.store.get_metric(names[0], names[1], names[2])
