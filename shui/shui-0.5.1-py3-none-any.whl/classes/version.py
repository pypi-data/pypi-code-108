"""Class to contain information about a Spark/Hadoop version"""
import re
from packaging.version import parse as version_parse


class Version:
    """Class to contain information about a Spark/Hadoop version"""

    regex = re.compile("spark-([0-9.]*)-bin-hadoop([0-9.]*).tgz$")

    def __init__(self, filename, url):
        self.filename = filename
        self.url = url

    @property
    def spark(self):
        """Spark version"""
        return self.regex.match(self.filename).group(1)

    @property
    def hadoop(self):
        """Hadoop version"""
        return self.regex.match(self.filename).group(2)

    def __str__(self):
        return f"<comment>Spark</comment> (<info>{self.spark}</info>) <comment>Hadoop</comment> (<info>{self.hadoop}</info>)"

    def __repr__(self):
        return f"<Version {self.filename} {self.url}>"

    def __lt__(self, other):
        if version_parse(self.spark) != version_parse(other.spark):
            return version_parse(self.spark) < version_parse(other.spark)
        return version_parse(self.hadoop) < version_parse(other.hadoop)
