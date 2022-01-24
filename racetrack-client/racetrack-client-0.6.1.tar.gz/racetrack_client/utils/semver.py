import re


class SemanticVersion:
    """
    Version numbering adhering to Semantic Versioning Specification (SemVer)
    It should match `MAJOR.MINOR.PATCH[LABEL]` format, eg.:
    - 1.2.3
    - 10.0.1-alpha
    - 0.0.0-dev
    """

    version_pattern = re.compile(r'(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<label>.*)')

    def __init__ (self, vstring):
        match = self.version_pattern.fullmatch(vstring)
        if not match:
            raise ValueError(f"Version '{vstring}' doesn't match SemVer format 'X.Y.Z[-label]'")
        self.major = int(match.group('major'))
        self.minor = int(match.group('minor'))
        self.patch = int(match.group('patch'))
        self.label = match.group('label')

    def __str__ (self):
        return f'{self.major}.{self.minor}.{self.patch}{self.label}'

    def _compare(self, other) -> int:
        """
        Returns zero if objects are considered "equal",
        negative if self is less than other, otherwise return positive.
        """
        if isinstance(other, str):
            other = SemanticVersion(other)

        if self.major != other.major:
            return self.major - other.major
        if self.minor != other.minor:
            return self.minor - other.minor
        if self.patch != other.patch:
            return self.patch - other.patch

        return self._compare_labels(self.label, other.label)

    def __eq__(self, other):
        return self._compare(other) == 0

    def __lt__(self, other):
        return self._compare(other) < 0

    def __le__(self, other):
        return self._compare(other) <= 0

    def __gt__(self, other):
        return self._compare(other) > 0

    def __ge__(self, other):
        return self._compare(other) >= 0

    @staticmethod
    def _compare_labels(label1: str, label2: str) -> int:
        if label1 == label2:
            return 0
        # According to Semver, pre-release version has lower precedence than a normal version
        # Example: 1.0.0-alpha < 1.0.0.
        if not label2:
            return -1
        if not label1:
            return 1

        if label1 < label2:
            return -1
        else:
            return 1
