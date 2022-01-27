import re


def split_camel(name):
    return re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', name)

class ValidationError(Exception):
    pass

class Validator(object):

    def __init__(self, submitter):
        self._submitter = submitter
        self.errors = set()
        self.warnings = set()
        self.notices = set()

    def add_error(self, msg):
        self.errors.add("[{}]:\n{}".format(self.title(), msg))

    def add_warning(self, msg):
        self.warnings.add("[{}]:\n{}".format(self.title(), msg))

    def add_notice(self, msg):
        self.notices.add("[{}]:\n{}".format(self.title(), msg))

    def run(self, layername):
        raise NotImplementedError

    @classmethod
    def plugins(cls):
        return cls.__subclasses__()

    @classmethod
    def title(cls):
        return split_camel(cls.__name__)
