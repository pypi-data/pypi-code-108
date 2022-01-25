import logging

from stram.utils.hashing import get_image_hash
from stram.utils.json_processing import dict2json, json2namespace

logger = logging.getLogger(__name__)


class Worklog:
    """
    Entity that keeps track of grid search over styling parameters for a given
    pair of `content_image` and `style_image`.

    Args:
        content_image (np.ndarray): the image to apply the style on (uint8)
        style_image (np.ndarray): the image whose style to apply (uint8)
        filepath (str): the path to the already serialized worklog instance
    """

    def __init__(self, content_image=None, style_image=None, filepath=None):
        if filepath is not None:
            self.load_from_filepath(filepath)
        elif content_image is not None and style_image is not None:
            self.content_hash = get_image_hash(content_image)
            self.style_hash = get_image_hash(style_image)
            self.table = {}
        else:
            self.content_hash = None
            self.style_hash = None
            self.table = {}

    @classmethod
    def new(cls, content_image, style_image):
        """
        Create a new worklog instance. It happens when starting a new grid search
        on a pair of images.

        Args:
            content_image (np.ndarray): the image to apply the style on (uint8)
            style_image (np.ndarray): the image whose style to apply (uint8)
        """
        return cls(content_image=content_image, style_image=style_image)

    @classmethod
    def from_file(cls, filepath):
        """
        Load worklog instance from file. It happens when resuming work
        on a pair of images.

        Args:
            filepath (str): the path to the already serialized worklog instance
        """
        return cls(filepath=filepath)

    def __eq__(self, other):
        return (
            self.content_hash == other.content_hash
            and self.style_hash == other.style_hash
            and set(self.table.keys()) == set(other.table.keys())
        )

    def save_to_filepath(self, filepath):
        """
        Serialize worklog as a json file.

        Args:
            filepath (str): path to the serialized json
        """
        dict_to_serialize = dict(
            content_hash=self.content_hash, style_hash=self.style_hash, table=self.table
        )
        dict2json(dict_to_serialize, filepath)

    def load_from_filepath(self, filepath):
        """
        Load worklog from a serialized json.

        Args:
            filepath (str): path to the serialized json
        """
        config = json2namespace(filepath)
        self.content_hash = config.content_hash
        self.style_hash = config.style_hash
        self.table = config.table

    def add_work_unit(self, unit_hash, unit_config):
        """
        Add a unit of work to the logs.

        Args:
            unit_hash (str): the hash value of the styling config
            unit_config (Bunch): the styling configurations
        """
        if unit_hash in self.table:
            logger.warning('Overwriting unit of work in the worklog')
        self.table[unit_hash] = unit_config
