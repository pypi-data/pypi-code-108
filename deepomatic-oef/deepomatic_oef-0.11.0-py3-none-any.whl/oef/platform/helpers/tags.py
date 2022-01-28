from enum import Enum

from .common import CHECK_LIST


###############################################################################

class Tag(Enum):
    """
    Tags are used to handle control's visibility.
    """
    @classmethod
    def name(cls):
        return cls.__name__.lower()


###############################################################################

class Backend(Tag):
    TENSORFLOW = 'tensorflow'
    DARKNET = 'darknet'


class ViewType(Tag):
    CLASSIFICATION = 'CLA'
    TAGGING = 'TAG'
    DETECTION = 'DET'


###############################################################################

class Tags:

    def __init__(self, tags):
        """
        Defines a list of tags.

        Args:
            tags (list): a list of instance of Tag
        """
        CHECK_LIST(tags, Tag)
        self._tags = {}
        for tag in tags:
            assert tag.name() not in self._tags
            self._tags[tag.name()] = tag.value

    @property
    def tags(self):
        return self._tags
