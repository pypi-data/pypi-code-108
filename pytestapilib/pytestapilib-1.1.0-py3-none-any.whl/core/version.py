from packaging.version import parse


class VersionParser:

    SKIP_REASON = 'improper version'

    def __init__(self, required_version: str, actual_version: str):
        self.required_version = required_version
        self.actual_version = actual_version

    def is_not_deployed(self):
        return parse(self.actual_version) < parse(self.required_version)
