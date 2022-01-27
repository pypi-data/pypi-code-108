import abc
import logging
from v_m_b.ImageRepository.ImageRepositoryBase import ImageRepositoryBase
from v_m_b.VolumeInfo.VolInfo import VolInfo

#
# Super magic constant.
# See https://github.com/archive-ops/scripts/processing/sync2archive.sh
#


class VolumeInfoBase(metaclass=abc.ABCMeta):
    """
    Gets volume info for a work.
    Passes request off to subclasses
    """

    logger: logging = None

    def __init__(self, repo: ImageRepositoryBase):
        """
        :param boto_client: context for operations
        :type boto_client: boto3.client
        : param bucket: target container
        :type bucket: boto.s3.bucket.Bucket
        """
        self._repo = repo
        self.logger = logging.getLogger(__name__)

    @abc.abstractmethod
    def fetch(self, urlRequest) -> [VolInfo]:
        """
        Subclasses implement
        :param urlRequest:
        :return: VolInfo[] with  one entry for each image in the image group
        """
        pass

    @staticmethod
    def getImageGroup(image_group_id: str) -> str:
        """
        :param image_group_id:
        :type image_group_id: str
        Some old image groups in eXist are encoded Innn, but their real name on disk is
        RID-nnnn. this detects their cases, and returns the disk folder they actually
        exist in. This is a stupid gross hack, we should either fix the archive repository, or have the
        BUDA and/or eXist APIs adjust for this.
        """
        pre, rest = image_group_id[0], image_group_id[1:]
        if pre == 'I' and rest.isdigit() and len(rest) == 4:
            suffix = rest
        else:
            suffix = image_group_id
        return suffix

    def getImageNames(self, work_rid: str, image_group: str, bom_name: str) -> []:
        """
        get names of the image files (actually, all the files in an image group, regardless
        :param work_rid: work name ex: W1FPl2251
        :param image_group: sub folder (e.g. I1CZ0085)
        :param bom_name: name of container of file list
        :return: str[]  should contain ['I1CZ0085001.jpg','I1CZ0085002.jpg'...']
        """
        return self._repo.getImageNames(work_rid, image_group, bom_name)
