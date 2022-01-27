from collections import namedtuple

ExperimentModel = namedtuple('ExperimentModel', ['id', 'name', 'condition', 'is_archived', 'flags', 'labels', 'stickinessProperty'])
