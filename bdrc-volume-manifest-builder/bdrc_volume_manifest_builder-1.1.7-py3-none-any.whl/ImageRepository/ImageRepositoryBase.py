"""
Base class for image repositories
"""

from abc import ABCMeta, abstractmethod
import logging
from typing import Tuple

from v_m_b.VolumeInfo.VolInfo import VolInfo


class ImageRepositoryBase(metaclass=ABCMeta):

    @abstractmethod
    def manifest_exists(self, work_Rid: str, image_group_name: str) -> bool:
        """
        Test if a manifest exists
        :param work_Rid: work identifier
        :param image_group_name: which image group (volume)
        :return: true if the args point to a path containing a 'dimensions.json' object
        """
        pass

    @abstractmethod
    def generateManifest(self, work_Rid: str, vol_infos: VolInfo) -> []:
        """
        Generates the manifest for one image group. The manifest contains entries for each image.
        See manifestCommons.fillBlobDataWithImage
        :param work_Rid: Work name
        :type work_Rid: str
        :param vol_infos: data structure of volumes
        :type vol_infos: VolInfo
        :return: manifest as list of dictionaries
        """
        pass

    @abstractmethod
    def uploadManifest(self, work_rid: str, image_group: str, bom_name: str,  manifest_zip: bytes):
        """
        Uploads a zip string of a manifest object
        :param work_rid: locator
        :param image_group: locator
        :param bom_name: filename of target
        :param manifest_zip: payload
        :type manifest_zip: bytes
        :return:
        """

    @abstractmethod
    def getImageNames(self, work_rid: str, image_group: str, bom_name: str) -> []:
        """
        get names of the image files (actually, all the files in an image group, regardless
        :param work_rid: work name ex: W1FPl2251
        :param image_group: sub folder (e.g. I1CZ0085)
        :param bom_name: name of container of file list
        :return: str[]  should contain ['I1CZ0085001.jpg','I1CZ0085002.jpg'...']
        """
        pass

    @abstractmethod
    def getPathfromLocators(self, work_Rid: str, image_group_folder_name: str):
        """
        :param work_Rid: Work resource id
        :param image_group_folder_name: image group - gets transformed
        :returns:  the s3 prefix (~folder) in which the volume will be present.
        """

    @abstractmethod
    def resolveWork(self, work_rid_path: str) -> Tuple[str, str]:
        """
        split the work_rid_path into a directory and a path.
        Implementation-defined
        :param work_rid_path:
        :return: the path and the work_rid
        """
        pass

    @staticmethod
    def fullPath(in_path: str) -> str:
        """
        Returns a fully qualitfied path according to the OS. Useful for resolving environment vars
        :param in_path: path to expand
        :return: expanded path, resolving user home specifiers and environment variables
        """
        import os
        return os.path.expanduser(os.path.expandvars(in_path))

    # RO property
    @property
    def repo_log(self) -> object:
        return self._log

    def __init__(self, bom: str):
        """
        :param bom: key to bill of materials
        :type bom: str
        """
        self._bom = bom
        self._log = logging.getLogger(__name__)
